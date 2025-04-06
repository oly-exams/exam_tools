from django.http import Http404
from django.shortcuts import get_object_or_404

from ipho_exam import qml
from ipho_exam.models import Language, PDFNode, Question, TranslationNode, VersionNode


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
        qwp.node = VersionNode.objects.filter(
            question=qwp.question, language=qwp.lang, status__in=status
        ).first()
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
