# coding=utf-8
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
        body = render_to_string('ipho_exam/tex/exam_cover.tex', RequestContext(HttpRequest(), cover)).encode("utf-8")
        compile_task = tasks.compile_tex.s(body, [])
        all_tasks.append(compile_task)

    for question in questions:
        for sl in student_languages:
            if question.is_answer_sheet() and not sl.with_answer:
                continue

            print 'Prepare', question, 'in', sl.language
            trans = qquery.latest_version(question.pk, sl.language.pk) ## TODO: simplify latest_version, because question and language are already in memory
            if not trans.lang.is_pdf:
                trans_content, ext_resources = trans.qml.make_tex()
                for r in ext_resources:
                    if isinstance(r, tex.FigureExport):
                        r.lang = sl.language
                ext_resources.append(tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls'))
                context = {
                            'polyglossia' : sl.language.polyglossia,
                            'font'        : fonts.noto[sl.language.font],
                            'extraheader' : sl.language.extraheader,
                            'lang_name'   : u'{} ({})'.format(sl.language.name, sl.language.delegation.country),
                            'title'       : u'{} - {}'.format(question.exam.name, question.name),
                            'is_answer'   : question.is_answer_sheet(),
                            'document'    : trans_content,
                          }
                body = render_to_string('ipho_exam/tex/exam_question.tex', RequestContext(HttpRequest(), context)).encode("utf-8")
                compile_task = tasks.compile_tex.s(body, ext_resources)
            else:
                compile_task = tasks.serve_pdfnode.s(trans.node.pdf.read())
            if question.is_answer_sheet():
                bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, sl.student)
                barcode_task = tasks.add_barcode.s(bgenerator)
                all_tasks.append( celery.chain(compile_task, barcode_task) )
            else:
                all_tasks.append(compile_task)
        exam_id = question.exam.pk
        position = question.position

    filename = u'{}_EXAM-{}-{}.pdf'.format(sl.student.code, exam_id, position)
    chord_task = celery.chord(all_tasks, tasks.concatenate_documents.s(filename))
    if commit:
        final_task = celery.chain(
            chord_task,
            tasks.identity_args.s(),
            tasks.commit_compiled_exam.s()
        )
        task = final_task
    else:
        task = chord_task
    return task
