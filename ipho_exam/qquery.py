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

from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404

from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string

from copy import deepcopy
from collections import OrderedDict


from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, PDFNode, Language, Figure, Feedback, StudentSubmission, ExamAction
from ipho_exam import qml


class Qwrapper(object):
    pass

def latest_version(question_id, lang_id):
    q = Qwrapper()

    q.question = get_object_or_404(Question, id=question_id)
    q.lang = get_object_or_404(Language, id=lang_id)

    if q.lang.is_pdf:
        q.node = get_object_or_404(PDFNode, question=q.question, language=q.lang)
        return q

    if q.lang.versioned:
        q.node = VersionNode.objects.filter(question=q.question, language=q.lang, status='C').order_by('-version')[0]
    else:
        q.node = get_object_or_404(TranslationNode, question=q.question, language=q.lang)

    q.qml = qml.make_qml(q.node) if '<question' in q.node.text else qml.QMLquestion('<question id="q0" />')

    return q

def get_version(question_id, lang_id, version_num):
    q = Qwrapper()

    q.question = get_object_or_404(Question, id=question_id)
    q.lang = get_object_or_404(Language, id=lang_id)
    q.node = get_object_or_404(VersionNode, question=q.question, language=q.lang, version=version_num)

    q.qml = qml.make_qml(q.node) if '<question' in q.node.text else qml.QMLquestion('<question id="q0" />')

    return q
