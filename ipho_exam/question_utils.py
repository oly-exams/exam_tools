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

import os
import celery

from django.http import HttpRequest
from django.template.loader import render_to_string
from django.conf import settings

from ipho_exam import tasks
from ipho_exam import tex, pdf, qquery, fonts, iphocode


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
        "code": "{}{}".format("Z", question.position),
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
