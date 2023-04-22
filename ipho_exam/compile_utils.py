# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
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
    get_ppnt_on_stud_exam,
)
from ipho_exam import tex, pdf, qquery, fonts, iphocode

OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")
EVENT_TEMPLATE_PATH = getattr(settings, "EVENT_TEMPLATE_PATH")


## utils
def all_same(items):
    return all(x == items[0] for x in items)


def generate_exam(  # pylint: disable=too-many-arguments
    question,
    participant,
    language,
    all_barcodes,
    all_docs,
    meta,
    start_page=0,
    qrcode=True,
):
    """helper function that prepares documents, compiles them and
    returns a list with all pdfs. Does not add a QR code if qrcode is
    set to False.

    Args:
        question (ipho_exam.models.Question): question.
        participant (ipho_exam.models.Participant): participant.
        language (ipho_exam.models.Language): language for participant.
        all_barcodes (list): list of iphocode.Question.BarcodeGen that
            have a QR code.
        all_docs (list): list of bytes with pdf content.
        meta (dict): dictionary that contains information, e.g.,
            about number of pages.
        start_page (int, optional): Index (number - 1) of the first page.
        qrcode (bool, optional): If False, does not add a QR code to
            document. If True, adds a QR code to answer sheets.

    Returns:
        all_barcodes, all_docs, meta: see in Args.
    """
    print(f"Prepare {question} in {language} for {participant}.")
    trans = qquery.latest_version(
        question.pk, language.pk
    )  ## TODO: simplify latest_version, because question and language are already in memory
    if not trans.lang.is_pdf or question.exam.flags & question.exam.FLAG_SQUASHED:
        trans_content, ext_resources = trans.qml.make_tex()
        for reso in ext_resources:
            if isinstance(reso, tex.FigureExport):
                reso.lang = language
        ext_resources.append(
            tex.TemplateExport(
                os.path.join(EVENT_TEMPLATE_PATH, "tex_resources", "ipho2016.cls")
            )
        )
        context = {
            "polyglossia": language.polyglossia,
            "polyglossia_options": language.polyglossia_options,
            "font": fonts.ipho[language.font],
            "extraheader": language.extraheader,
            "lang_name": f"{language.name} ({language.delegation.country})",
            "exam_name": f"{question.exam.name}",
            "code": (
                f"{question.code}{int(bool(question.position))}"
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
        print(f"Compile {question} {language}.")
        question_pdf = pdf.compile_tex(body, ext_resources)
    else:
        question_pdf = trans.node.pdf.read()

    doc_pages = pdf.get_num_pages(question_pdf)
    meta["num_pages"] += doc_pages
    meta["last_num_pages"] = doc_pages
    if question.is_answer_sheet() and qrcode:
        bgenerator = iphocode.QuestionBarcodeGen(
            question.exam, question, participant, startnum=start_page
        )
        page = pdf.add_barcode(question_pdf, bgenerator)
        meta["barcode_num_pages"] += doc_pages
        all_barcodes.append(bgenerator.base)
        all_docs.append(page)
    else:
        bgenerator = iphocode.QuestionBarcodeGen(
            question.exam,
            question,
            participant,
            startnum=start_page,
            suppress_code=True,
        )
        page = pdf.add_barcode(question_pdf, bgenerator)
        all_docs.append(page)

    if question.is_answer_sheet() and question.working_pages > 0:
        context = {
            "polyglossia": "english",
            "polyglossia_options": "",
            "font": fonts.ipho["notosans"],
            "extraheader": "",
            # 'lang_name'   : u'{} ({})'.format(language.name, language.delegation.country),
            "exam_name": f"{question.exam.name}",
            "code": (
                f"W{int(bool(question.position))}"
                if question.exam.flags & question.exam.FLAG_SQUASHED
                else f"W{question.position}"
            ),
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
                    os.path.join(EVENT_TEMPLATE_PATH, "tex_resources", "ipho2016.cls")
                )
            ],
        )
        bgenerator = iphocode.QuestionBarcodeGen(
            question.exam, question, participant, qcode="W", suppress_code=not qrcode
        )
        page = pdf.add_barcode(question_pdf, bgenerator)

        doc_pages = pdf.get_num_pages(page)
        meta["num_pages"] += doc_pages
        meta["barcode_num_pages"] += doc_pages
        all_barcodes.append(bgenerator.base)
        all_docs.append(page)

    return all_barcodes, all_docs, meta


def participant_exam_document(
    questions,
    participant_languages,
    cover=None,
    job_task=None,
    question_lang_list=None,
    answer_lang_list=None,
):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    meta = {}
    meta["num_pages"] = 0
    meta["last_num_pages"] = 0
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
        if settings.INCLUDE_COVER:
            all_docs.append(page)

    # XXX: for now, no support for both squashed exam AND groups.

    if questions[0].exam.flags & questions[0].exam.FLAG_SQUASHED:
        groups = (
            (k, list(g)) for k, g in itertools.groupby(questions, key=lambda q: q.code)
        )
        qpl = (
            (q, p)
            for (__, g), p in itertools.product(groups, participant_languages)
            for q in g
        )
    else:
        qpl = itertools.product(questions, participant_languages)

    start_page = 0
    state = (None, None)

    for question, ppnt_l in qpl:
        if question.exam.flags & question.exam.FLAG_SQUASHED:
            if state != (question.code, ppnt_l):
                state = (question.code, ppnt_l)
                start_page = 0

        if question.is_answer_sheet() and not ppnt_l.with_answer:
            continue
        if question.is_question_sheet() and (not ppnt_l.with_question or ppnt.is_group):
            continue
        all_barcodes, all_docs, meta = generate_exam(
            question,
            ppnt_l.participant,
            ppnt_l.language,
            all_barcodes,
            all_docs,
            meta,
            start_page,
        )

        # add a second set of answer sheets for the group with draft watermark
        if question.is_answer_sheet() and ppnt.is_group:
            start = len(all_docs)
            all_barcodes, all_docs, meta = generate_exam(
                question,
                ppnt_l.participant,
                ppnt_l.language,
                all_barcodes,
                all_docs,
                meta,
                qrcode=False,
            )
            for i in range(start, len(all_docs)):
                all_docs[i] = pdf.add_watermark(
                    all_docs[i], watermark_filename="watermark_draft.pdf"
                )

        if question.exam.flags & question.exam.FLAG_SQUASHED:
            start_page += meta["last_num_pages"]

    if ppnt.is_group:  # pylint: disable=too-many-nested-blocks
        # generate documents for students
        for student in ppnt.students.all():
            for question in questions:
                stud_ppnt = get_ppnt_on_stud_exam(question.exam, student)
                if question.is_question_sheet():
                    if student in question_lang_list:
                        for lang in question_lang_list[student]:
                            all_barcodes, all_docs, meta = generate_exam(
                                question,
                                stud_ppnt,
                                lang,
                                all_barcodes,
                                all_docs,
                                meta,
                                qrcode=False,
                            )
                elif question.is_answer_sheet():
                    if student in answer_lang_list:
                        for lang in answer_lang_list[student]:
                            all_barcodes, all_docs, meta = generate_exam(
                                question,
                                stud_ppnt,
                                lang,
                                all_barcodes,
                                all_docs,
                                meta,
                                qrcode=False,
                            )

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
                timeout=30,
            )
            req.raise_for_status()  # or, if r.status_code == requests.codes.ok:
            doc_task.delete()
            print(
                f"Doc committed: {ppnt_l.participant.code} {exam_code}{position}"  # pylint: disable=undefined-loop-variable
            )
        except DocumentTask.DoesNotExist:
            pass
    return final_doc, meta
