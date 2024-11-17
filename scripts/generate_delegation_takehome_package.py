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

import shutil
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exam_tools.settings")
sys.path.append(".")

import django
django.setup()

import argparse
import re
import time
from hashlib import md5
from io import BytesIO

import celery
import ipho_exam
from celery.result import AsyncResult
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from ipho_core.models import Delegation
from ipho_exam import fonts, qquery, tasks, tex
from ipho_exam.models import Exam, Language, Question
from PyPDF2 import PdfFileMerger, PdfFileReader

OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")
EVENT_TEMPLATE_PATH = getattr(settings, "EVENT_TEMPLATE_PATH")

BASE_PATH = "downloads/delegations_private_dirs/"  # inside media folder
FONT_PATH = os.path.join(settings.STATIC_PATH, "noto")
REPLACEMENTS = [(settings.STATIC_PATH, ".")]

CACHE_PREFIX = getattr(settings, "CACHE_CACHED_RESPONSES_PREFIX", "cached-responses")
CACHE_TIMEOUT = getattr(settings, "CACHE_CACHED_RESPONSES_TIMEOUT", 600)  # 10 min


def compile_tex_async(body, ext_resources=tuple(), filename="question.pdf"):
    etag = md5(body.encode("utf8")).hexdigest()
    cache_key = "{}:{}:{}".format(CACHE_PREFIX, "compile_tex", etag)
    task_id = cache.get(cache_key)

    if task_id is None:
        job = tasks.compile_tex.delay(body, ext_resources, filename, etag)
        task_id = job.id
        cache.set(cache_key, task_id, CACHE_TIMEOUT)
    return task_id

def compile_question_pdf(question, language, solution):
    try:
        trans = qquery.latest_version(question.pk, language.pk)
    except:
        return
    trans_content, ext_resources = trans.qml.make_tex()
    # Remove the solution if we don't want it
    if not solution:
        solution_env_pattern = r"\\begin{QTS}{[^}]*}.*?\\end{QTS}"
        trans_content = re.sub(solution_env_pattern, "", trans_content, flags=re.DOTALL)
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
    try:
        task = AsyncResult(compile_tex_async(body, ext_resources))
        while not task.ready():
            time.sleep(1)
        if task.ready():
            pdf, _ = task.get()
            return pdf
    except Exception as e:
        print("WARNING")
        print(e)
        return False


def compile_question_tex(question, language, delegation, logo_file, solution):
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
    # Remove the solution if we don't want it
    if not solution:
        solution_env_pattern = r"\\begin{QTS}{[^}]*}.*?\\end{QTS}"
        trans_content = re.sub(solution_env_pattern, "", trans_content, flags=re.DOTALL)
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

        base_folder = "{}_private/takehome/tex/{}_{}_{}_{}_tex/".format(
            delegation.name,
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


def generate_delegation(logo_file, exams, delegation, combine_exams, solution):
    delegation_takehome_pdf_dir = os.path.join(
        settings.DOCUMENT_PATH, BASE_PATH, f"{delegation.name}_private/takehome/pdf"
    )
    os.makedirs(delegation_takehome_pdf_dir, exist_ok=True)
    for exam in exams:
        # The position filter is only really needed if there are spare problems
        questions = Question.objects.filter(
            exam=exam  # , position__in=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
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
        for lang in languages:
            # Only official EN has solution if any
            if solution and not lang.delegation.name == OFFICIAL_DELEGATION:
                continue
            merger = PdfFileMerger()
            for q in questions:
                compile_question_tex(q, lang, delegation, logo_file, solution)
                if combine_exams:
                    pdf = False
                    tries = 0
                    while not pdf and tries < 10: # Max 10 retries if compilation fails
                        pdf = compile_question_pdf(q, lang, solution)
                        tries += 1
                        if pdf:
                            pdfdoc = PdfFileReader(
                                BytesIO(pdf)
                            )
                            merger.append(pdfdoc)
                else:
                    question_pdf = compile_question_pdf(q, lang, solution)
                    base_filename = "{}_{}_{}_{}_{}.pdf".format(
                        exam.code,
                        q.position,
                        slugify(q.name),
                        slugify(lang.name),
                        delegation.name,
                    )
                    filename = os.path.join(delegation_takehome_pdf_dir, base_filename)
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    with open(filename, "wb") as fp:
                        fp.write(question_pdf)
            if combine_exams:
                base_filename = (
                    f"{exam.code}_{slugify(lang.name)}_{delegation.name}_{'solution' if solution else ''}.pdf"
                )
                filename = os.path.join(delegation_takehome_pdf_dir, base_filename)
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                merger.write(filename)
                merger.close()

            print(f"Completed language {lang} for delegation {delegation.name}")
        print(f"Completed exam {exam} for delegation {delegation.name}")


def generate_all(logo_file, exam_names=None, combine_exams=False, solution=False):
    delegations = Delegation.objects.exclude(name=OFFICIAL_DELEGATION).all()
    if exam_names == None:
        exams = Exam.objects.all()
    else:
        exams = Exam.objects.filter(name__in=exam_names)

    if not exams:
        print(f"ERROR: no exams corresponding to {exam_names}.")
        return

    for d in delegations:
        generate_delegation(logo_file, exams, d, combine_exams, solution=False)
        if solution:
            generate_delegation(logo_file, exams, d, combine_exams, solution=True)
        base_folder = os.path.join(str(d.name) + "_private", "takehome")
        shutil.make_archive(
            os.path.join(
                settings.DOCUMENT_PATH, BASE_PATH, str(d.name) + "_private", "takehome"
            ),
            "zip",
            root_dir=os.path.join(settings.DOCUMENT_PATH, BASE_PATH),
            base_dir=base_folder,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("logo_file", help="Filename of the logo file image in templates")
    parser.add_argument("--filter_exams", help="Name of the exam(s) to use")
    parser.add_argument("--combine", help="Combine exams to one pdf", action="store_true")
    parser.add_argument("--solution", help="Include solutions", action="store_true")
    args = parser.parse_args()
    generate_all(
        logo_file=args.logo_file,
        combine_exams=args.combine,
        exam_names=args.filter_exams.split(",") if args.filter_exams else None,
        solution=args.solution
    )
