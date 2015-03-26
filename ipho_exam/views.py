# coding=utf-8
from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.templatetags.static import static


from ipho_exam.models import Exam, Question


def index(request):
    return render_to_response('ipho_exam/index.html',
                              context_instance=RequestContext(request))

def editor(request, exam_id=None, question_id=None, lang_id=None, orig_id=0, orig_v=None):
    context = {'exam_id'     : exam_id,
               'question_id' : question_id,
               'lang_id'     : question_id,
               'orig_id'     : orig_id,
               'orig_v'      : orig_v,
               }
    exam_list = Exam.objects.filter(hidden=False) # TODO: allow admin to see all exams
    context['exam_list'] = exam_list
    
    if exam_id is not None:
        exam = Exam.objects.get(id=exam_id)
        context['exam'] = exam
    if question_id is not None:
        question = Question.objects.get(id=question_id)
        context['question'] = question
    elif exam is not None and exam.question_set.count() > 0:
        question = exam.question_set.all()[0]
        context['question'] = question
    
    
    return render(request, 'ipho_exam/editor.html', context)

