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

#!/usr/bin/env python

from __future__ import print_function, unicode_literals

from builtins import range
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'
import itertools

import django
django.setup()
from django.conf import settings
from django.http import HttpRequest
from django.template import RequestContext
from django.template.loader import render_to_string

from ipho_core.models import Delegation
from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, PDFNode, Language, Figure, Feedback, StudentSubmission, ExamAction, Place
from ipho_exam import qml, tex, pdf, qquery, fonts, iphocode

import ipho_exam
from ipho_exam import tasks

OFFICIAL_LANGUAGE = 1
OFFICIAL_DELEGATION = getattr(settings, 'OFFICIAL_DELEGATION')


def compile_question(question, language):
    print('Prepare', question, 'in', language)
    try:
        trans = qquery.latest_version(question.pk, language.pk)
    except:
        print('NOT-FOUND')
        return
    trans_content, ext_resources = trans.qml.make_tex()
    for r in ext_resources:
        if isinstance(r, tex.FigureExport):
            r.lang = language
    ext_resources.append(tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls'))
    context = {
        'polyglossia': language.polyglossia,
        'polyglossia_options': language.polyglossia_options,
        'font': fonts.ipho[language.font],
        'extraheader': language.extraheader,
        'lang_name': u'{} ({})'.format(language.name, language.delegation.country),
        'exam_name': u'{}'.format(question.exam.name),
        'code': u'{}{}'.format(question.code, question.position),
        'title': u'{} - {}'.format(question.exam.name, question.name),
        'is_answer': question.is_answer_sheet(),
        'document': trans_content.encode('utf-8'),
    }
    body = render_to_string('ipho_exam/tex/exam_question.tex', RequestContext(HttpRequest(), context))
    print('Compile...')
    try:
        question_pdf = pdf.compile_tex(body, ext_resources)
        exam_code = question.exam.code
        position = question.position
        question_code = question.code

        filename = u'TRANSLATION-{}{}-{}-{}-{}.pdf'.format(
            exam_code, position, question_code, language.delegation.name, language.name.replace(u' ', u'_')
        )
        with open(filename, 'wb') as fp:
            fp.write(question_pdf)
        print(filename, 'DONE')
    except Exception as e:
        print('ERROR')
        print(e)


def compile_stud_exam_question(questions, student_languages, cover=None, commit=False):
    all_tasks = []
    all_docs = []
    if cover is not None:
        body = render_to_string('ipho_exam/tex/exam_cover.tex', RequestContext(HttpRequest(), cover))
        question_pdf = pdf.compile_tex(body, [])
        q = questions[0]
        s = student_languages[0].student
        bgenerator = iphocode.QuestionBarcodeGen(q.exam, q, s, qcode='C')
        page = pdf.add_barcode(question_pdf, bgenerator)

        all_docs.append(page)

    for question in questions:
        for sl in student_languages:
            if question.is_answer_sheet() and not sl.with_answer:
                continue

            print('Prepare', question, 'in', sl.language)
            trans = qquery.latest_version(
                question.pk, sl.language.pk
            )  ## TODO: simplify latest_version, because question and language are already in memory
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
            body = render_to_string('ipho_exam/tex/exam_question.tex', RequestContext(HttpRequest(), context))
            print('Compile', question, sl.language)
            question_pdf = pdf.compile_tex(body, ext_resources)

            if question.is_answer_sheet():
                bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, sl.student)
                page = pdf.add_barcode(question_pdf, bgenerator)
                all_docs.append(page)
            else:
                all_docs.append(question_pdf)

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
                body = render_to_string('ipho_exam/tex/exam_blank.tex', RequestContext(HttpRequest(), context))
                question_pdf = pdf.compile_tex(body, [tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls')])
                bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, sl.student, qcode='W')
                page = pdf.add_barcode(question_pdf, bgenerator)
                all_docs.append(page)

        exam_id = question.exam.pk
        position = question.position

    filename = u'{}_EXAM-{}-{}.pdf'.format(sl.student.code, exam_id, position)
    final_doc = pdf.concatenate_documents(all_docs)
    with open(filename, 'wb') as fp:
        fp.write(final_doc)
    print(filename, 'DONE')


def generate_extra_sheets(student, question, startnum, npages):
    context = {
        'polyglossia': 'english',
        'polyglossia_options': '',
        'font': fonts.ipho['notosans'],
        'exam_name': u'{}'.format(question.exam.name),
        'code': u'{}{}'.format('Z', question.position),
        'pages': list(range(npages)),
        'startnum': startnum + 1,
    }
    body = render_to_string('ipho_exam/tex/exam_blank.tex', RequestContext(HttpRequest(), context))
    question_pdf = pdf.compile_tex(body, [tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls')])
    bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, student, qcode='Z', startnum=startnum)
    doc_pdf = pdf.add_barcode(question_pdf, bgenerator)
    return doc_pdf


## Main functions


def missing_submissions():
    missing = Delegation.objects.filter(
        exam_status__exam__name='Experiment',
        exam_status__action=ExamAction.TRANSLATION,
        exam_status__status=ExamAction.OPEN
    ).exclude(name=settings.OFFICIAL_DELEGATION)

    exam = Exam.objects.get(name='Experiment')
    questions = exam.question_set.all()
    grouped_questions = {k: list(g) for k, g in itertools.groupby(questions, key=lambda q: q.position)}

    for d in missing:
        students = d.student_set.all()
        for student in students:
            student_seat = Place.objects.get(student=student, exam=exam)
            for position, qgroup in list(grouped_questions.items()):
                student_languages = StudentSubmission.objects.filter(exam=exam, student=student)
                cover_ctx = {'student': student, 'exam': exam, 'question': qgroup[0], 'place': student_seat.name}
                compile_stud_exam_question(questions, student_languages, cover=cover_ctx, commit=False)


def compile_all():
    exams = Exam.objects.filter(name='Theory')
    questions = Question.objects.filter(exam=exams, position__in=[1, 2, 3])
    languages = Language.objects.filter(studentsubmission__exam=exams).distinct()
    print('Going to compile in {} languages.'.format(len(languages)))
    for q in questions:
        for lang in languages:
            compile_question(q, lang)
    print('COMPLETED')


if __name__ == '__main__':
    compile_all()
