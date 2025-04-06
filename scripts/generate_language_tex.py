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

BASE_PATH = "../media/downloads/language_tex"
FONT_PATH = os.path.join(settings.STATIC_PATH, "noto")
REPLACEMENTS = [(settings.STATIC_PATH, ".")]


def compile_question(question, language, logo_file):
    if language.is_pdf:
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
        # folder = u'Translation-{}{}-{}-{}-{}'.format(
        #    exam_code, position, question_code, language.delegation.name, language.name.replace(u' ', u'_')
        # )
        folder = "TRANSLATION_{}_{}/{}_{}_{}/".format(
            language.delegation.name,
            slugify(language.name),
            slugify(question.exam.name),
            slugify(question.position),
            slugify(question.name),
        )

        base_folder = folder
        folder = os.path.join(BASE_PATH, folder)
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
        shutil.make_archive(folder, "zip", root_dir=BASE_PATH, base_dir=base_folder)
    except Exception as e:
        print("ERROR", e)


def export_all(logo_file, names=("Theory", "Experiment")):
    exams = Exam.objects.filter(name__in=names)
    # The position filter is only really needed if there are spare problems
    questions = Question.objects.filter(
        exam__in=exams, position__in=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    )
    languages = Language.objects.filter(
        participantsubmission__participant__exam__in=exams
    ).distinct()
    print(f"Going to export in {len(languages)} languages.")
    for q in questions:
        for lang in languages:
            compile_question(q, lang, logo_file)
    print("COMPLETED")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        export_all(logo_file="icho2022_logo.png", names=sys.argv[1:])
    else:
        export_all(logo_file="icho2022_logo.png")
