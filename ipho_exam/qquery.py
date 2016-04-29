from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404

from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string

from copy import deepcopy
from collections import OrderedDict


from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, PDFNode, Language, Figure, Feedback, StudentSubmission, ExamDelegationSubmission
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

    q.qml = qml.QMLquestion(q.node.text if '<question' in q.node.text else '<question id="" />')

    return q
