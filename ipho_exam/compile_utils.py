# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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


import itertools
import os
from hashlib import md5
import requests

from django.http import HttpRequest
from django.urls import reverse

from django.template.loader import render_to_string

from django.conf import settings

from ipho_exam.models import (
    DocumentTask,
)
from ipho_exam import tex, pdf, qquery, fonts, iphocode

OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")
EVENT_TEMPLATE_PATH = getattr(settings, "EVENT_TEMPLATE_PATH")


## utils
def all_same(items):
    return all(x == items[0] for x in items)


def participant_exam_document(
    questions, participant_languages, cover=None, job_task=None
):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    meta = {}
    meta["num_pages"] = 0
    meta["barcode_num_pages"] = 0
    meta["barcode_base"] = ""
    meta["etag"] = ""
    meta["filename"] = ""
    all_barcodes = []
    all_docs = []
    if cover is not None:
        suppress_cover_code = not settings.CODE_ON_COVER_SHEET
        body = render_to_string(
            os.path.join(EVENT_TEMPLATE_PATH, "tex", "exam_cover.tex"),
            request=HttpRequest(),
            context=cover,
        )
        question_pdf = pdf.compile_tex(body, [])
        que = questions[0]
        ppnt = participant_languages[0].participant
        bgenerator = iphocode.QuestionBarcodeGen(
            que.exam, que, ppnt, qcode="C", suppress_code=suppress_cover_code
        )
        page = pdf.add_barcode(question_pdf, bgenerator)
        doc_pages = pdf.get_num_pages(page)
        meta["num_pages"] += doc_pages
        if not suppress_cover_code:
            meta["barcode_num_pages"] += doc_pages
        all_barcodes.append(bgenerator.base)
        all_docs.append(page)

    if questions[0].exam.flags & questions[0].exam.FLAG_SQUASHED:
        qp = ((q, p) for p, q in itertools.product(participant_languages, questions))
    else:
        qp = itertools.product(questions, participant_languages)

    start_page = 0
    state = (None, None)

    for question, ppnt_l in qp:
        if question.exam.flags & question.exam.FLAG_SQUASHED:
            if state != (question.type, ppnt_l):
                state = (question.type, ppnt_l)
                start_page = 0

        if question.is_answer_sheet() and not ppnt_l.with_answer:
            continue
        if question.is_question_sheet() and not ppnt_l.with_question:
            continue

        print(f"Prepare {question} in {ppnt_l.language}.")
        trans = qquery.latest_version(
            question.pk, ppnt_l.language.pk
        )  ## TODO: simplify latest_version, because question and language are already in memory
        if not trans.lang.is_pdf or question.exam.flags & question.exam.FLAG_SQUASHED:
            trans_content, ext_resources = trans.qml.make_tex()
            for reso in ext_resources:
                if isinstance(reso, tex.FigureExport):
                    reso.lang = ppnt_l.language
            ext_resources.append(
                tex.TemplateExport(
                    os.path.join(
                        EVENT_TEMPLATE_PATH, "tex_resources", "ipho2016.cls"
                    )
                )
            )
            context = {
                "polyglossia": ppnt_l.language.polyglossia,
                "polyglossia_options": ppnt_l.language.polyglossia_options,
                "font": fonts.ipho[ppnt_l.language.font],
                "extraheader": ppnt_l.language.extraheader,
                "lang_name": f"{ppnt_l.language.name} ({ppnt_l.language.delegation.country})",
                "exam_name": f"{question.exam.name}",
                "code": (
                    question.code
                    if question.exam.flags & question.exam.FLAG_SQUASHED
                    else f"{question.code}{question.position}"
                ),
                "title": f"{question.exam.name} - {question.name}",
                "is_answer": question.is_answer_sheet(),
                "document": trans_content,
                "startnum": start_page + 1,
            }
            body = render_to_string(
                os.path.join(EVENT_TEMPLATE_PATH, "tex", "exam_question.tex"),
                request=HttpRequest(),
                context=context,
            )
            print(f"Compile {question} {ppnt_l.language}.")
            question_pdf = pdf.compile_tex(body, ext_resources)
        else:
            question_pdf = trans.node.pdf.read()

        doc_pages = pdf.get_num_pages(question_pdf)
        meta["num_pages"] += doc_pages
        if question.exam.flags & question.exam.FLAG_SQUASHED:
            start_page += doc_pages
        if question.is_answer_sheet():
            bgenerator = iphocode.QuestionBarcodeGen(
                question.exam, question, ppnt_l.participant, startnum=start_page
            )
            page = pdf.add_barcode(question_pdf, bgenerator)
            meta["barcode_num_pages"] += doc_pages
            all_barcodes.append(bgenerator.base)
            all_docs.append(page)
        else:
            bgenerator = iphocode.QuestionBarcodeGen(
                question.exam, question, ppnt_l.participant, startnum=start_page, suppress_code=True
            )
            page = pdf.add_barcode(question_pdf, bgenerator)
            all_docs.append(page)

        if question.is_answer_sheet() and question.working_pages > 0:
            context = {
                "polyglossia": "english",
                "polyglossia_options": "",
                "font": fonts.ipho["notosans"],
                "extraheader": "",
                # 'lang_name'   : u'{} ({})'.format(ppnt_l.language.name, ppnt_l.language.delegation.country),
                "exam_name": f"{question.exam.name}",
                "code": "{}{}".format("W", question.position),
                "title": f"{question.exam.name} - {question.name}",
                "is_answer": question.is_answer_sheet(),
                "pages": list(range(question.working_pages)),
            }
            body = render_to_string(
                os.path.join(EVENT_TEMPLATE_PATH, "tex", "exam_blank.tex"),
                request=HttpRequest(),
                context=context,
            )
            question_pdf = pdf.compile_tex(
                body,
                [
                    tex.TemplateExport(
                        os.path.join(
                            EVENT_TEMPLATE_PATH, "tex_resources", "ipho2016.cls"
                        )
                    )
                ],
            )
            bgenerator = iphocode.QuestionBarcodeGen(
                question.exam, question, ppnt_l.participant, qcode="W"
            )
            page = pdf.add_barcode(question_pdf, bgenerator)

            doc_pages = pdf.get_num_pages(page)
            meta["num_pages"] += doc_pages
            meta["barcode_num_pages"] += doc_pages
            all_barcodes.append(bgenerator.base)
            all_docs.append(page)

        exam_id = question.exam.pk
        exam_code = question.exam.code
        position = question.position

    if all_same(all_barcodes):
        meta["barcode_base"] = all_barcodes[0] or None
    else:
        meta["barcode_base"] = ",".join(all_barcodes)

    filename = f"{ppnt_l.participant.code}_EXAM-{exam_id}-{position}.pdf"  # pylint: disable=undefined-loop-variable
    final_doc = pdf.concatenate_documents(all_docs)
    meta["filename"] = filename
    meta["etag"] = md5(final_doc).hexdigest()
    if job_task is not None:
        try:
            doc_task = DocumentTask.objects.get(task_id=job_task)
            doc = doc_task.document
            api_url = settings.SITE_URL + reverse(
                "api-exam:document-detail", kwargs=dict(pk=doc.pk)
            )
            req = requests.patch(
                api_url,
                allow_redirects=False,
                headers={"ApiKey": settings.EXAM_TOOLS_API_KEYS["PDF Worker"]},
                files={"file": (meta["filename"], final_doc)},
                data={
                    "num_pages": meta["num_pages"],
                    "barcode_num_pages": meta["barcode_num_pages"],
                    "barcode_base": meta["barcode_base"],
                },
            )
            req.raise_for_status()  # or, if r.status_code == requests.codes.ok:
            doc_task.delete()
            print(
                f"Doc committed: {ppnt_l.participant.code} {exam_code}{position}"  # pylint: disable=undefined-loop-variable
            )
        except DocumentTask.DoesNotExist:
            pass
    return final_doc, meta
