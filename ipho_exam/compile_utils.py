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
import os
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.core.urlresolvers import reverse

from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string
from django.core.files.base import ContentFile

from django.conf import settings
from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, PDFNode, Language, Figure, Feedback, StudentSubmission, ExamAction, DocumentTask
from ipho_exam import qml, tex, pdf, qquery, fonts, iphocode
from hashlib import md5
import requests

OFFICIAL_LANGUAGE = 1
OFFICIAL_DELEGATION = getattr(settings, 'OFFICIAL_DELEGATION')
TEX_TEMPLATE_PATH = getattr(settings, 'TEX_TEMPLATE_PATH')


## utils
def all_same(items):
    return all(x == items[0] for x in items)


def student_exam_document(questions, student_languages, cover=None, job_task=None):
    meta = {}
    meta['num_pages'] = 0
    meta['barcode_num_pages'] = 0
    meta['barcode_base'] = ''
    meta['etag'] = ''
    meta['filename'] = ''
    all_barcodes = []
    all_docs = []
    if cover is not None:
        suppress_cover_code = not settings.CODE_ON_COVER_SHEET
        body = render_to_string(os.path.join(TEX_TEMPLATE_PATH, 'tex', 'exam_cover.tex'), request=HttpRequest(), context=cover)
        question_pdf = pdf.compile_tex(body, [])
        q = questions[0]
        s = student_languages[0].student
        bgenerator = iphocode.QuestionBarcodeGen(q.exam, q, s, qcode='C', suppress_code=suppress_cover_code)
        page = pdf.add_barcode(question_pdf, bgenerator)
        doc_pages = pdf.get_num_pages(page)
        meta['num_pages'] += doc_pages
        if not suppress_cover_code:
            meta['barcode_num_pages'] += doc_pages
        all_barcodes.append(bgenerator.base)
        all_docs.append(page)

    for question in questions:
        for sl in student_languages:
            if question.is_answer_sheet() and not sl.with_answer:
                continue

            print('Prepare {} in {}.'.format(question, sl.language))
            trans = qquery.latest_version(
                question.pk, sl.language.pk
            )  ## TODO: simplify latest_version, because question and language are already in memory
            if not trans.lang.is_pdf:
                trans_content, ext_resources = trans.qml.make_tex()
                for r in ext_resources:
                    if isinstance(r, tex.FigureExport):
                        r.lang = sl.language
                ext_resources.append(tex.TemplateExport(os.path.join(TEX_TEMPLATE_PATH, 'tex_resources', 'ipho2016.cls')))
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
                body = render_to_string(os.path.join(TEX_TEMPLATE_PATH, 'tex', 'exam_question.tex'), request=HttpRequest(), context=context)
                print('Compile {} {}.'.format(question, sl.language))
                question_pdf = pdf.compile_tex(body, ext_resources)
            else:
                question_pdf = trans.node.pdf.read()

            doc_pages = pdf.get_num_pages(question_pdf)
            meta['num_pages'] += doc_pages
            if question.is_answer_sheet():
                bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, sl.student)
                page = pdf.add_barcode(question_pdf, bgenerator)
                meta['barcode_num_pages'] += doc_pages
                all_barcodes.append(bgenerator.base)
                all_docs.append(page)
            else:
                bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, sl.student, suppress_code=True)
                page = pdf.add_barcode(question_pdf, bgenerator)
                all_docs.append(page)

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
                body = render_to_string(os.path.join(TEX_TEMPLATE_PATH, 'tex', 'exam_blank.tex'), request=HttpRequest(), context=context)
                question_pdf = pdf.compile_tex(body, [tex.TemplateExport(os.path.join(TEX_TEMPLATE_PATH, 'tex_resources', 'ipho2016.cls'))])
                bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, sl.student, qcode='W')
                page = pdf.add_barcode(question_pdf, bgenerator)

                doc_pages = pdf.get_num_pages(page)
                meta['num_pages'] += doc_pages
                meta['barcode_num_pages'] += doc_pages
                all_barcodes.append(bgenerator.base)
                all_docs.append(page)

        exam_id = question.exam.pk
        exam_code = question.exam.code
        position = question.position

    if all_same(all_barcodes):
        meta['barcode_base'] = all_barcodes[0] or None
    else:
        meta['barcode_base'] = ','.join(all_barcodes)

    filename = u'{}_EXAM-{}-{}.pdf'.format(sl.student.code, exam_id, position)
    final_doc = pdf.concatenate_documents(all_docs)
    meta['filename'] = filename
    meta['etag'] = md5(final_doc).hexdigest()
    if job_task is not None:
        try:
            doc_task = DocumentTask.objects.get(task_id=job_task)
            doc = doc_task.document
            api_url = settings.SITE_URL + reverse('api-exam:document-detail', kwargs=dict(pk=doc.pk))
            r = requests.patch(
                api_url,
                allow_redirects=False,
                headers={'ApiKey': settings.EXAM_TOOLS_API_KEYS['PDF Worker']},
                files={'file': (meta['filename'], final_doc)},
                data={
                    'num_pages': meta['num_pages'],
                    'barcode_num_pages': meta['barcode_num_pages'],
                    'barcode_base': meta['barcode_base'],
                }
            )
            r.raise_for_status()  # or, if r.status_code == requests.codes.ok:
            doc_task.delete()
            print('Doc committed: {} {}{}'.format(sl.student.code, exam_code, position))
        except DocumentTask.DoesNotExist:
            pass
    return final_doc, meta
