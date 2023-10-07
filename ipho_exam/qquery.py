# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
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

from django.shortcuts import get_object_or_404
from django.http import Http404

from ipho_exam.models import (
    Question,
    VersionNode,
    TranslationNode,
    PDFNode,
    Language,
)
from ipho_exam import qml


class Qwrapper:
    pass


def latest_version(question_id, lang_id, user=None, status=None):
    # pylint: disable=attribute-defined-outside-init

    if status is None:
        status = ["C"]

    qwp = Qwrapper()

    if user is not None:
        qwp.question = get_object_or_404(
            Question.objects.for_user(user), id=question_id
        )
    else:
        qwp.question = get_object_or_404(Question, id=question_id)
    qwp.lang = get_object_or_404(Language, id=lang_id)

    if qwp.lang.is_pdf:
        qwp.node = get_object_or_404(PDFNode, question=qwp.question, language=qwp.lang)
        return qwp

    if qwp.lang.versioned:
        qwp.node = (
            VersionNode.objects.filter(
                question=qwp.question, language=qwp.lang, status__in=status
            )
            .first()
        )
        if qwp.node is None:
            raise Http404("No VersionNode found.")
    else:
        qwp.node = get_object_or_404(
            TranslationNode, question=qwp.question, language=qwp.lang
        )

    qwp.qml = (
        qml.make_qml(qwp.node)
        if "<question" in qwp.node.text
        else qml.create_empty_qml_question()
    )

    return qwp


def get_version(question_id, lang_id, version_num, user=None):
    # pylint: disable=attribute-defined-outside-init
    qwp = Qwrapper()

    if user is not None:
        qwp.question = get_object_or_404(
            Question.objects.for_user(user), id=question_id
        )
    else:
        qwp.question = get_object_or_404(Question, id=question_id)
    qwp.lang = get_object_or_404(Language, id=lang_id)
    qwp.node = get_object_or_404(
        VersionNode, question=qwp.question, language=qwp.lang, version=version_num
    )

    qwp.qml = (
        qml.make_qml(qwp.node)
        if "<question" in qwp.node.text
        else qml.create_empty_qml_question()
    )

    return qwp
