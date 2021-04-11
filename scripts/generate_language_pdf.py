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

#!/usr/bin/env python


import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
import itertools
import sys

sys.path.append(".")

import django

django.setup()
from django.conf import settings
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify

from ipho_core.models import Delegation
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
    Place,
)
from ipho_exam import qml, tex, pdf, qquery, fonts, iphocode

import ipho_exam
from ipho_exam import tasks

OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")
EVENT_TEMPLATE_PATH = getattr(settings, "EVENT_TEMPLATE_PATH")


def compile_question(question, language):
    print("Prepare", question, "in", language)
    try:
        trans = qquery.latest_version(question.pk, language.pk)
    except:
        print("NOT-FOUND")
        return
    trans_content, ext_resources = trans.qml.make_tex()
    for r in ext_resources:
        if isinstance(r, tex.FigureExport):
            r.lang = language
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
        "code": f"{question.code}{question.position}",
        "title": f"{question.exam.name} - {question.name}",
        "is_answer": question.is_answer_sheet(),
        "document": trans_content,
    }
    body = render_to_string(
        os.path.join(EVENT_TEMPLATE_PATH, "tex", "exam_question.tex"),
        request=HttpRequest(),
        context=context,
    )
    print("Compile...")
    try:
        question_pdf = pdf.compile_tex(body, ext_resources)
        exam_code = question.exam.code
        position = question.position
        question_code = question.code

        filename = "../media/downloads/language_pdf/{}_{}/TRANSLATION_{}_{}.pdf".format(
            slugify(question.exam.name),
            slugify(question.name),
            language.delegation.name,
            slugify(language.name),
        )
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as fp:
            fp.write(question_pdf)
        print(filename, "DONE")
    except Exception as e:
        print("ERROR")
        print(e)


def compile_stud_exam_question(questions, student_languages, cover=None, commit=False):
    all_tasks = []
    all_docs = []
    if cover is not None:
        body = render_to_string(
            os.path.join(EVENT_TEMPLATE_PATH, "tex", "exam_cover.tex"),
            request=HttpRequest(),
            context=cover,
        )
        question_pdf = pdf.compile_tex(body, [])
        q = questions[0]
        s = student_languages[0].student
        bgenerator = iphocode.QuestionBarcodeGen(
            q.exam, q, s, qcode="C", suppress_code=True
        )
        page = pdf.check_add_barcode(question_pdf, bgenerator)

        all_docs.append(page)

    for question in questions:
        for sl in student_languages:
            if question.is_answer_sheet() and not sl.with_answer:
                continue

            print("Prepare", question, "in", sl.language)
            trans = qquery.latest_version(
                question.pk, sl.language.pk
            )  ## TODO: simplify latest_version, because question and language are already in memory
            trans_content, ext_resources = trans.qml.make_tex()
            for r in ext_resources:
                if isinstance(r, tex.FigureExport):
                    r.lang = sl.language
            ext_resources.append(
                tex.TemplateExport(
                    os.path.join(EVENT_TEMPLATE_PATH, "tex_resources", "ipho2016.cls")
                )
            )
            context = {
                "polyglossia": sl.language.polyglossia,
                "polyglossia_options": sl.language.polyglossia_options,
                "font": fonts.ipho[sl.language.font],
                "extraheader": sl.language.extraheader,
                "lang_name": f"{sl.language.name} ({sl.language.delegation.country})",
                "exam_name": f"{question.exam.name}",
                "code": f"{question.code}{question.position}",
                "title": f"{question.exam.name} - {question.name}",
                "is_answer": question.is_answer_sheet(),
                "document": trans_content,
            }
            body = render_to_string(
                os.path.join(EVENT_TEMPLATE_PATH, "tex", "exam_question.tex"),
                request=HttpRequest(),
                context=context,
            )
            print("Compile", question, sl.language)
            question_pdf = pdf.compile_tex(body, ext_resources)

            if question.is_answer_sheet():
                bgenerator = iphocode.QuestionBarcodeGen(
                    question.exam, question, sl.student
                )
                page = pdf.check_add_barcode(question_pdf, bgenerator)
                all_docs.append(page)
            else:
                all_docs.append(question_pdf)

            if question.is_answer_sheet() and question.working_pages > 0:
                context = {
                    "polyglossia": "english",
                    "polyglossia_options": "",
                    "font": fonts.ipho["notosans"],
                    "extraheader": "",
                    # 'lang_name'   : u'{} ({})'.format(sl.language.name, sl.language.delegation.country),
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
                    question.exam, question, sl.student, qcode="W"
                )
                page = pdf.check_add_barcode(question_pdf, bgenerator)
                all_docs.append(page)

        exam_id = question.exam.pk
        position = question.position

    filename = (
        "../media/downloads/language_pdf/{}_{}/student_exams/EXAM__{}.pdf".format(
            slugify(question.exam.name), slugify(question.name), sl.student.code
        )
    )
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    final_doc = pdf.concatenate_documents(all_docs)
    with open(filename, "wb") as fp:
        fp.write(final_doc)
    print(filename, "DONE")


def generate_extra_sheets(student, question, startnum, npages):
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
        question.exam, question, student, qcode="Z", startnum=startnum
    )
    doc_pdf = pdf.check_add_barcode(question_pdf, bgenerator)
    return doc_pdf


## Main functions


def missing_submissions():
    missing = Delegation.objects.filter(
        exam_status__exam__name="Experiment",
        exam_status__action=ExamAction.TRANSLATION,
        exam_status__status=ExamAction.OPEN,
    ).exclude(name=settings.OFFICIAL_DELEGATION)

    exam = Exam.objects.get(name="Experiment")
    questions = exam.question_set.all()
    grouped_questions = {
        k: list(g) for k, g in itertools.groupby(questions, key=lambda q: q.position)
    }

    for d in missing:
        students = d.student_set.all()
        for student in students:
            student_seat = Place.objects.get(student=student, exam=exam)
            for position, qgroup in list(grouped_questions.items()):
                student_languages = StudentSubmission.objects.filter(
                    exam__in=exam, student=student
                )
                cover_ctx = {
                    "student": student,
                    "exam": exam,
                    "question": qgroup[0],
                    "place": student_seat.name,
                }
                compile_stud_exam_question(
                    questions, student_languages, cover=cover_ctx, commit=False
                )


def compile_all(names=("Theory", "Experiment")):
    exams = Exam.objects.filter(name__in=names)
    questions = Question.objects.filter(exam__in=exams, position__in=[0, 1, 2, 3])
    languages = Language.objects.filter(studentsubmission__exam__in=exams).distinct()
    print("Going to compile in {} languages.".format(len(languages)))
    for q in questions:
        for lang in languages:
            compile_question(q, lang)
    print("COMPLETED")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        compile_all(names=sys.argv[1:])
    else:
        compile_all()
