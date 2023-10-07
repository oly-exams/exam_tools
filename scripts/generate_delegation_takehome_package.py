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
import shutil
import sys

sys.path.append(".")

import django

django.setup()
import celery
from celery.result import AsyncResult
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string

import ipho_exam
from ipho_core.models import Delegation
from ipho_exam import fonts, iphocode, pdf, qml, qquery, tasks, tex
from ipho_exam.models import Exam, Language, Question

OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")
EVENT_TEMPLATE_PATH = getattr(settings, "EVENT_TEMPLATE_PATH")

BASE_PATH = "downloads/delegation_takehome_package/"  # inside media folder
FONT_PATH = os.path.join(settings.STATIC_PATH, "noto")
REPLACEMENTS = [(settings.STATIC_PATH, ".")]


def compile_question_pdf(question, language, delegation):
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

        base_filename = "{}/{}{}_{}_{}_{}.pdf".format(
            slugify(delegation.country),
            question.exam.code,
            question.position,
            slugify(question.name),
            slugify(language.name),
            language.delegation.name,
        )
        filename = os.path.join(settings.DOCUMENT_PATH, BASE_PATH, base_filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as fp:
            fp.write(question_pdf)
        print(filename, "DONE")
    except Exception as e:
        print("ERROR")
        print(e)


def compile_question_tex(question, language, delegation, logo_file):
    if language.is_pdf:
        print("LANGUAGE IS PDF")
        return
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
        "STATIC_PATH": ".",
    }
    body = render_to_string(
        os.path.join(EVENT_TEMPLATE_PATH, "tex", "exam_question.tex"),
        request=HttpRequest(),
        context=context,
    ).replace(FONT_PATH, ".")
    try:
        exam_code = question.exam.code
        position = question.position
        question_code = question.code

        base_folder = "{}/{}{}_{}_{}_{}_tex/".format(
            slugify(delegation.country),
            question.exam.code,
            question.position,
            slugify(question.name),
            slugify(language.name),
            language.delegation.name,
        )
        folder = os.path.join(settings.DOCUMENT_PATH, BASE_PATH, base_folder)
        os.makedirs(folder, exist_ok=True)

        with open(os.path.join(folder, "question.tex"), "w") as f:
            for r in REPLACEMENTS:
                body = body.replace(*r)
            f.write(body)

        for e in ext_resources:
            e.save(dirname=folder)

        # replacing font path in ipho2016.cls
        with open(os.path.join(folder, "ipho2016.cls")) as f:
            tex_cls = f.read()
        for r in REPLACEMENTS:
            tex_cls = tex_cls.replace(*r)
        with open(os.path.join(folder, "ipho2016.cls"), "w") as f:
            f.write(tex_cls)

        used_fonts = [
            v
            for k, v in list(fonts.ipho[language.font].items())
            if isinstance(v, str) and v.endswith(".ttf")
        ]
        used_fonts.extend(
            [
                v
                for k, v in list(fonts.ipho["notosans"].items())
                if isinstance(v, str) and v.endswith(".ttf")
            ]
        )
        used_fonts = set(used_fonts)

        font_folder = os.path.join(folder, "noto")
        os.makedirs(font_folder, exist_ok=True)
        for f in used_fonts:
            source = os.path.join(FONT_PATH, f)
            shutil.copyfile(source, os.path.join(font_folder, f))

        for f in os.listdir(folder):
            if f.endswith(".pdf.svg"):
                os.remove(os.path.join(folder, f))
        shutil.copyfile(
            os.path.join(settings.STATIC_PATH, logo_file),
            os.path.join(folder, logo_file),
        )
    except Exception as e:
        print("ERROR", e)


def generate_delegation(logo_file, exams, delegation):
    for exam in exams:
        # The position filter is only really needed if there are spare problems
        questions = Question.objects.filter(
            exam=exam, position__in=[1, 2, 3, 4, 5, 6, 7, 8, 9]
        )
        languages = Language.objects.filter(
            participantsubmission__participant__exam=exam, delegation=delegation
        ).distinct()
        languages = languages.union(
            Language.objects.filter(delegation__name=OFFICIAL_DELEGATION).distinct()
        )

        print(
            f"Going to export exam {exam} in {len(languages)} languages for delegation {delegation}."
        )
        for q in questions:
            for lang in languages:
                compile_question_tex(q, lang, delegation, logo_file)
                compile_question_pdf(q, lang, delegation)
    print("COMPLETED")


def generate_all(logo_file, exam_names=("Theory", "Experiment")):
    delegations = Delegation.objects.exclude(name=OFFICIAL_DELEGATION).all()
    exams = Exam.objects.filter(name__in=exam_names)

    if not exams:
        print(f"ERROR: no exams corresponding to {exam_names}.")
        return

    for d in delegations:
        generate_delegation(logo_file, exams, d)
        base_folder = slugify(d.country)
        shutil.make_archive(
            os.path.join(settings.DOCUMENT_PATH, BASE_PATH, base_folder),
            "zip",
            root_dir=os.path.join(settings.DOCUMENT_PATH, BASE_PATH),
            base_dir=base_folder,
        )


if __name__ == "__main__":
    if len(sys.argv) > 2:
        generate_all(logo_file=sys.argv[1], exam_names=sys.argv[2:])
    elif len(sys.argv) > 1:
        generate_all(logo_file=sys.argv[1])
    else:
        print(
            "You need to provide at least one argument with the name of the logo file."
        )
