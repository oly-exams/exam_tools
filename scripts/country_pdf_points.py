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


import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import django

django.setup()
from django.conf import settings

from django.shortcuts import get_object_or_404
from django.http import HttpRequest

from django.urls import reverse
from django.core.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string
from django.db.models import Sum

from django.conf import settings
from ipho_core.models import Delegation, Student
from ipho_exam.models import (
    Exam,
    Question,
    VersionNode,
    TranslationNode,
    PDFNode,
    Language,
    Figure,
    Feedback,
    StudentSubmission,
    ExamAction,
)
from ipho_marking.models import Marking, MarkingMeta
from ipho_exam import qml, tex, pdf, qquery, fonts, iphocode

OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")


def compile_all():
    for delegation in Delegation.objects.exclude(name=settings.OFFICIAL_DELEGATION):
        students = Student.objects.filter(delegation=delegation).values(
            "id", "pk", "code", "first_name", "last_name"
        )
        vid = "F"
        points_per_student = []
        for student in students:
            stud_exam_points_list = (
                Marking.objects.filter(version=vid, student=student["id"])
                .values("marking_meta__question")
                .annotate(exam_points=Sum("points"))
                .values("exam_points")
                .order_by("marking_meta__question__exam", "marking_meta__question")
            )
            total = sum(
                [
                    st_points["exam_points"]
                    for st_points in stud_exam_points_list
                    if st_points["exam_points"] is not None
                ]
            )
            points_per_student.append((student, stud_exam_points_list, total))

        exams = (
            MarkingMeta.objects.filter(question__exam__hidden=False)
            .values("question__exam")
            .annotate(exam_points=Sum("max_points"))
            .values(
                "question__exam__code",
                "question__position",
                "question__exam__name",
                "exam_points",
            )
            .order_by("question__exam", "question")
            .distinct()
        )

        results = ""
        results += "\\vspace{2em}\n\\begin{center}\n"
        results += (
            "\\begin{tabular}{"
            + "".join(["p{3cm}"] + ["p{1cm}"] * (len(exams) + 1))
            + "}\n"
        )
        for i, ex in enumerate(exams):
            results += " & "
            results += "\\textbf{{{}-{}}}".format(
                ex["question__exam__code"], ex["question__position"]
            )
        results += " & \\textbf{Total} \\\\\n"
        for (student, stud_exam_points_list, total) in points_per_student:
            results += "{} & ".format(student["code"])
            for p in stud_exam_points_list:
                results += "{} & ".format(p["exam_points"])
            results += f"{total} \\\\\n"
        results += "\\end{tabular}\n"
        results += "\\end{center}\n"

        context = {
            "polyglossia": "english",
            "polyglossia_options": "",
            "font": fonts.ipho["notosans"],
            "extraheader": "",
            "delegation": delegation,
            "results": results,
        }
        body = render_to_string(
            "ipho_marking/tex/exam_points.tex", request=HttpRequest(), context=context
        )
        with open(f"FINALPOINTS-{delegation.name}.tex", "w") as fp:
            fp.write(body)
        continue
        filename = f"FINALPOINTS-{delegation.name}.pdf"
        print("Compile", filename)
        question_pdf = pdf.compile_tex(body, [])
        # question_pdf = pdf.compile_tex(body, ext_resources)
        print("Compile Success")
        with open(filename, "wb") as fp:
            fp.write(question_pdf)
        print(filename, "DONE")


if __name__ == "__main__":
    compile_all()
