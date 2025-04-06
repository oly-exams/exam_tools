#!/usr/bin/env python


import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import django

django.setup()
from crispy_forms.utils import render_crispy_form
from django.conf import settings
from django.core.context_processors import csrf
from django.db.models import Sum
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse

from ipho_core.models import Delegation
from ipho_exam import fonts, iphocode, pdf, qml, qquery, tex
from ipho_exam.models import (
    Exam,
    ExamAction,
    Feedback,
    Figure,
    Language,
    Participant,
    ParticipantSubmission,
    PDFNode,
    Question,
    TranslationNode,
    VersionNode,
)
from ipho_marking.models import Marking, MarkingMeta

OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")


def compile_all():
    for delegation in Delegation.objects.exclude(name=settings.OFFICIAL_DELEGATION):
        participants = Participant.objects.filter(delegation=delegation).values(
            "id", "pk", "code", "first_name", "last_name"
        )
        vid = "F"
        points_per_participant = []
        for participant in participants:
            ppnt_exam_points_list = (
                Marking.objects.filter(version=vid, participant=participant["id"])
                .values("marking_meta__question")
                .annotate(exam_points=Sum("points"))
                .values("exam_points")
            )
            total = sum(
                st_points["exam_points"]
                for st_points in ppnt_exam_points_list
                if st_points["exam_points"] is not None
            )
            points_per_participant.append((participant, ppnt_exam_points_list, total))

        exams = (
            MarkingMeta.objects.filter(
                question__exam__visibility__gte=Exam.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT
            )
            .values("question__exam")
            .annotate(exam_points=Sum("max_points"))
            .values(
                "question__exam__code",
                "question__position",
                "question__exam__name",
                "exam_points",
            )
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
        for (participant, ppnt_exam_points_list, total) in points_per_participant:
            results += "{} & ".format(participant["code"])
            for p in ppnt_exam_points_list:
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
