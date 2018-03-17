# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
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

from __future__ import print_function

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'
import shutil

import django
django.setup()
from django.conf import settings

from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.template import RequestContext

from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string

from django.conf import settings
from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, PDFNode, Language, Figure, Feedback, StudentSubmission, ExamAction
from ipho_exam import qml, tex, pdf, qquery, fonts, iphocode

import ipho_exam
from ipho_exam import tasks
import celery
from celery.result import AsyncResult

OFFICIAL_LANGUAGE = 1
OFFICIAL_DELEGATION = getattr(settings, 'OFFICIAL_DELEGATION')

BASE_PATH = u'../media/language_tex'
REPLACEMENTS = [('/srv/exam_tools/app/static/noto', '.'), ('/srv/exam_tools/app/static', '.')]


def compile_question(question, language, logo_file):
    print('Prepare', question, 'in', language)
    try:
        trans = qquery.latest_version(question.pk, language.pk)
    except:
        print('NOT-FOUND')
        return
    trans_content, ext_resources = trans.qml.make_tex()
    for r in ext_resources:
        if isinstance(r, tex.FigureExport):
            r.lang = language
    ext_resources.append(tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls'))
    context = {
        'polyglossia': language.polyglossia,
        'polyglossia_options': language.polyglossia_options,
        'font': fonts.ipho[language.font],
        'extraheader': language.extraheader,
        'lang_name': u'{} ({})'.format(language.name, language.delegation.country),
        'exam_name': u'{}'.format(question.exam.name),
        'code': u'{}{}'.format(question.code, question.position),
        'title': u'{} - {}'.format(question.exam.name, question.name),
        'is_answer': question.is_answer_sheet(),
        'document': trans_content.encode('utf-8'),
        'STATIC_PATH': '.'
    }
    body = render_to_string('ipho_exam/tex/exam_question.tex',
                            RequestContext(HttpRequest(), context)).replace(u'/srv/exam_tools/app/static/noto',
                                                                            u'.').encode("utf-8")
    try:
        exam_code = question.exam.code
        position = question.position
        question_code = question.code
        folder = u'Translation-{}{}-{}-{}-{}'.format(
            exam_code, position, question_code, language.delegation.name, language.name.replace(u' ', u'_')
        )

        base_folder = folder
        folder = os.path.join(BASE_PATH, folder)
        try:
            os.makedirs(folder)
        except OSError:
            pass
        with open(os.path.join(folder, 'question.tex'), 'w') as f:
            for r in REPLACEMENTS:
                body = body.replace(*r)
            f.write(body)

        for e in ext_resources:
            e.save(dirname=folder)

        # replacing font path in ipho2016.cls
        with open(os.path.join(folder, 'ipho2016.cls'), 'r') as f:
            tex_cls = f.read()
        for r in REPLACEMENTS:
            tex_cls = tex_cls.replace(*r)
        with open(os.path.join(folder, 'ipho2016.cls'), 'w') as f:
            f.write(tex_cls)

        used_fonts = [
            v for k, v in list(fonts.ipho[language.font].items()) if isinstance(v, str) and v.endswith('.ttf')
        ]
        used_fonts.extend([
            v for k, v in list(fonts.ipho['notosans'].items()) if isinstance(v, str) and v.endswith('.ttf')
        ])
        used_fonts = set(used_fonts)

        for f in used_fonts:
            source = os.path.join('/srv/exam_tools/app/static/noto', f)
            shutil.copyfile(source, os.path.join(folder, f))

        for f in os.listdir(folder):
            if f.endswith('.pdf.svg'):
                os.remove(os.path.join(folder, f))

        shutil.copyfile('/srv/exam_tools/static/' + logo_file, os.path.join(folder, logo_file))
        shutil.make_archive(folder, 'zip', root_dir=BASE_PATH, base_dir=base_folder)
    except Exception as e:
        print('ERROR', e)


def export_all(logo_file):
    exams = Exam.objects.filter(name__in=['Theory', 'Experiment'])
    questions = Question.objects.filter(exam=exams, position__in=[1, 2, 3])
    languages = Language.objects.filter(studentsubmission__exam=exams).distinct()
    print('Going to export in {} languages.'.format(len(languages)))
    for q in questions:
        for lang in languages:
            compile_question(q, lang, logo_file)
    print('COMPLETED')


if __name__ == '__main__':
    export_all('apho17_logo_bw.pdf')
