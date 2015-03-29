# coding=utf-8
from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from django.templatetags.static import static

from copy import deepcopy

from ipho_core.models import Delegation

from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, Language
from ipho_exam import qml

from ipho_exam.forms import LanguageForm

OFFICIAL_LANGUAGE = 1

@login_required
def index(request):
    success = None
    
    delegation = Delegation.objects.filter(members=request.user)
    print delegation
    
    ## Language section
    own_lang = None
    language_form = None
    if delegation.count() > 0:
        own_lang = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
        print own_lang
        
        language_form = LanguageForm(request.POST or None)
        if language_form.is_valid():
            lang_model = language_form.save(commit=False)
            lang_model.save()
            lang_model.delegation = delegation
            lang_model.save()
            language_form = LanguageForm()
            success = '<strong>Language created!</strong> The new languages has successfully been created.'
    
    ## Exam section
    exam_list = Exam.objects.filter(hidden=False) # TODO: allow admin to see all exams
    
    
    return render(request, 'ipho_exam/index.html',
            {
                'language_form' : language_form,
                'own_lang'      : own_lang,
                'exam_list'     : exam_list,
                'success'       : success,
            })


@login_required
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
    content_set = None
    form     = None
    orig_lang = None
    trans_lang = None
    
    if exam_id is not None:
        exam = Exam.objects.get(id=exam_id)
    if question_id is not None:
        question = Question.objects.get(id=question_id)
    elif exam is not None and exam.question_set.count() > 0:
        question = exam.question_set.all()[0]
    
    delegation = Delegation.objects.filter(members=request.user)
    
    orig_lang = Language.objects.get(id=orig_id)
    all_lang = Language.objects.filter(hidden=False).order_by('name')
    if delegation.count() > 0:
        own_lang = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
    elif request.user.is_superuser:
        own_lang = Language.objects.filter().order_by('name')
        
    ## TODO:
    ## * check for read-only questions
    ## * deal with errors when node not found: no content
    
    if question:
    # try:
        ## TODO: make a free function
        if orig_lang.versioned:
            orig_node = VersionNode.objects.filter(question=question, language=orig_lang, status='C').order_by('-version')[0]
        else:
            orig_node = TranslationNode.objects.get(question=question, language=orig_lang)
        orig_q = qml.QMLquestion(orig_node.text)
        
        trans_content = {}
        if lang_id is not None:
            trans_lang = Language.objects.get(id=lang_id)
            trans_node, created = TranslationNode.objects.get_or_create(question=question, language_id=lang_id, defaults={'text': '', 'status' : 'O'}) ## TODO: check permissions for this.
            if len(trans_node.text) > 0:
                trans_q    = qml.QMLquestion(trans_node.text)
                trans_content = trans_q.get_content()
        
        form = qml.QMLForm(orig_q, trans_content, request.POST or None)
        content_set = qml.make_content(orig_q)
        
        if lang_id is not None and form.is_valid():
            ## update the content in the original XML.
            ## TODO: we could keep track of orig_v in the submission and, in case of updates, show a diff in the original language.
            q = deepcopy(orig_q)
            q.update(form.cleaned_data, set_blanks=True)
            trans_node.text = qml.xml2string(q.make_xml())
            trans_node.save()
    
    # except:
    #     context['warning'] = 'This question does not have any content.'
    
    context['exam']        = exam
    context['question']    = question
    context['all_lang']    = all_lang
    context['own_lang']    = own_lang
    context['orig_lang']   = orig_lang
    context['trans_lang']  = trans_lang
    context['content_set'] = content_set
    context['form']        = form
    return render(request, 'ipho_exam/editor.html', context)

