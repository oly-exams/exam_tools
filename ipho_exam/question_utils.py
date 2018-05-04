# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# coding=utf-8

from __future__ import print_function

from builtins import range
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.template import RequestContext

from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string

from django.conf import settings
from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, PDFNode, Language, Figure, Feedback, StudentSubmission, ExamAction
from ipho_exam import qml, tex, pdf, qquery, fonts, iphocode

import ipho_exam
from ipho_exam import tasks
import celery
from celery.result import AsyncResult

OFFICIAL_LANGUAGE = 1
OFFICIAL_DELEGATION = getattr(settings, 'OFFICIAL_DELEGATION')


def compile_stud_exam_question(questions, student_languages, cover=None, commit=False):
    all_tasks = []

    if cover is not None:
        body = render_to_string('ipho_exam/tex/exam_cover.tex', RequestContext(HttpRequest(), cover))
        compile_task = tasks.compile_tex.s(body, [])
        q = questions[0]
        s = student_languages[0].student
        bgenerator = iphocode.QuestionBarcodeGen(q.exam, q, s, qcode='C')
        barcode_task = tasks.add_barcode.s(bgenerator)
        all_tasks.append(celery.chain(compile_task, barcode_task))

    for question in questions:
        for sl in student_languages:
            if question.is_answer_sheet() and not sl.with_answer:
                continue

            print('Prepare', question, 'in', sl.language)
            trans = qquery.latest_version(
                question.pk, sl.language.pk
            )  ## TODO: simplify latest_version, because question and language are already in memory
            if not trans.lang.is_pdf:
                trans_content, ext_resources = trans.qml.make_tex()
                for r in ext_resources:
                    if isinstance(r, tex.FigureExport):
                        r.lang = sl.language
                ext_resources.append(tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls'))
                context = {
                    'polyglossia': sl.language.polyglossia,
                    'polyglossia_options': sl.language.polyglossia_options,
                    'font': fonts.ipho[sl.language.font],
                    'extraheader': sl.language.extraheader,
                    'lang_name': u'{} ({})'.format(sl.language.name, sl.language.delegation.country),
                    'exam_name': u'{}'.format(question.exam.name),
                    'code': u'{}{}'.format(question.code, question.position),
                    'title': u'{} - {}'.format(question.exam.name, question.name),
                    'is_answer': question.is_answer_sheet(),
                    'document': trans_content,
                }
                body = render_to_string('ipho_exam/tex/exam_question.tex', RequestContext(HttpRequest(),
                                                                                          context))
                compile_task = tasks.compile_tex.s(body, ext_resources)
            else:
                compile_task = tasks.serve_pdfnode.s(trans.node.pdf.read())
            if question.is_answer_sheet():
                bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, sl.student)
                barcode_task = tasks.add_barcode.s(bgenerator)
                all_tasks.append(celery.chain(compile_task, barcode_task))
            else:
                bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, sl.student, suppress_code=True)
                barcode_task = tasks.add_barcode.s(bgenerator)
                all_tasks.append(celery.chain(compile_task, barcode_task))

            if question.is_answer_sheet() and question.working_pages > 0:
                context = {
                    'polyglossia': 'english',
                    'polyglossia_options': '',
                    'font': fonts.ipho['notosans'],
                    'extraheader': '',
                    # 'lang_name'   : u'{} ({})'.format(sl.language.name, sl.language.delegation.country),
                    'exam_name': u'{}'.format(question.exam.name),
                    'code': u'{}{}'.format('W', question.position),
                    'title': u'{} - {}'.format(question.exam.name, question.name),
                    'is_answer': question.is_answer_sheet(),
                    'pages': list(range(question.working_pages)),
                }
                body = render_to_string('ipho_exam/tex/exam_blank.tex', RequestContext(HttpRequest(),
                                                                                       context))
                compile_task = tasks.compile_tex.s(body, [tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls')])
                bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, sl.student, qcode='W')
                barcode_task = tasks.add_barcode.s(bgenerator)
                all_tasks.append(celery.chain(compile_task, barcode_task))

        exam_id = question.exam.pk
        position = question.position

    filename = u'{}_EXAM-{}-{}.pdf'.format(sl.student.code, exam_id, position)
    chord_task = celery.chord(all_tasks, tasks.concatenate_documents.s(filename))
    if commit:
        final_task = celery.chain(chord_task, tasks.identity_args.s(), tasks.commit_compiled_exam.s())
        task = final_task
    else:
        task = chord_task
    return task


def generate_extra_sheets(student, question, startnum, npages, template_name='exam_blank.tex'):
    context = {
        'polyglossia': 'english',
        'polyglossia_options': '',
        'font': fonts.ipho['notosans'],
        'exam_name': u'{}'.format(question.exam.name),
        'code': u'{}{}'.format('Z', question.position),
        'pages': list(range(npages)),
        'startnum': startnum + 1,
    }
    body = render_to_string('ipho_exam/tex/{}'.format(template_name), RequestContext(HttpRequest(),
                                                                                     context))
    question_pdf = pdf.compile_tex(body, [tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls')])
    bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, student, qcode='Z', startnum=startnum)
    doc_pdf = pdf.add_barcode(question_pdf, bgenerator)
    return doc_pdf
