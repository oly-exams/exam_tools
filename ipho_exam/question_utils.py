import os

import celery
from django.conf import settings
from django.http import HttpRequest
from django.template.loader import render_to_string

from ipho_exam import fonts, iphocode, pdf, qquery, tasks, tex

OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")
EVENT_TEMPLATE_PATH = getattr(settings, "EVENT_TEMPLATE_PATH")


def generate_extra_sheets(
    participant, question, startnum, npages, template_name="exam_blank.tex"
):
    context = {
        "polyglossia": "english",
        "polyglossia_options": "",
        "font": fonts.ipho["notosans"],
        "exam_name": f"{question.exam.name}",
        "code": f"Z{question.position}",
        "pages": list(range(npages)),
        "startnum": startnum + 1,
    }
    body = render_to_string(
        os.path.join(EVENT_TEMPLATE_PATH, "tex", template_name),
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
        question.exam, question, participant, qcode="Z", startnum=startnum
    )
    doc_pdf = pdf.add_barcode(question_pdf, bgenerator)
    return doc_pdf
