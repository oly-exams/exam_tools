# coding=utf-8
from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.templatetags.static import static


from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, Language
from ipho_exam import qml

OFFICIAL_LANGUAGE = 1

def index(request):
    return render_to_response('ipho_exam/index.html',
                              context_instance=RequestContext(request))

def editor(request, exam_id=None, question_id=None, lang_id=None, orig_id=OFFICIAL_LANGUAGE, orig_v=None):
    context = {'exam_id'     : exam_id,
               'question_id' : question_id,
               'lang_id'     : question_id,
               'orig_id'     : orig_id,
               'orig_v'      : orig_v,
               }
    exam_list = Exam.objects.filter(hidden=False) # TODO: allow admin to see all exams
    context['exam_list'] = exam_list
    
    exam     = None
    question = None
    content  = None
    
    if exam_id is not None:
        exam = Exam.objects.get(id=exam_id)
    if question_id is not None:
        question = Question.objects.get(id=question_id)
    elif exam is not None and exam.question_set.count() > 0:
        question = exam.question_set.all()[0]
    
    lang = Language.objects.get(id=orig_id)
    
    
    ## TODO:
    ## * check for read-only questions
    ## * deal with errors when node not found: no content
    
    if question:
    # try:
        orig_node = None ## TODO: make a free function
        if lang.versioned:
            orig_node = VersionNode.objects.filter(question=question, language=lang, status='C').order_by('-version')[0]
        else:
            orig_node = TranslationNode.objects.get(question=question, language=lang)
        orig_q = qml.QMLquestion(orig_node.text)
        
        # trans_node = TranslationNode.objects.get(question=question, language_id=lang_id)
        # trans_q    = qml.QMLquestion(trans_node.text)
        # trans_content = trans_q.get_content()
        trans_content = {}
        
        content_set = qml.make_content(orig_q, trans_content)
        
    # except:
    #     context['warning'] = 'This question does not have any content.'
    
    context['exam']        = exam
    context['question']    = question
    context['content_set'] = content_set
    return render(request, 'ipho_exam/editor.html', context)

