# coding=utf-8
from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from crispy_forms.utils import render_crispy_form

from copy import deepcopy

from tempfile import mkdtemp
import subprocess
import os
import shutil
from hashlib import md5


from ipho_core.models import Delegation
from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, Language, Figure
from ipho_exam import qml, tex

from ipho_exam.forms import LanguageForm, FigureForm

OFFICIAL_LANGUAGE = 1

@login_required
@ensure_csrf_cookie
def index(request):
    success = None
    
    delegation = Delegation.objects.filter(members=request.user)
    
    own_lang   = None
    other_lang = None
    if delegation.count() > 0:
        own_lang = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
        other_lang = Language.objects.filter(hidden=False).exclude(delegation=delegation).order_by('name')
    else:
        other_lang = Language.objects.filter(hidden=False).order_by('name')
    
    ## Exam section
    exam_list = Exam.objects.filter(hidden=False) # TODO: allow admin to see all exams
    
    
    return render(request, 'ipho_exam/index.html',
            {
                'own_lang'      : own_lang,
                'other_lang'    : other_lang,
                'exam_list'     : exam_list,
                'success'       : success,
            })


@login_required
def add_language(request):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    delegation = Delegation.objects.get(members=request.user)
    
    ## Language section
    language_form = LanguageForm(request.POST or None)
    if language_form.is_valid():
        lang = language_form.instance.delegation = delegation
        lang = language_form.save()
        
        return JsonResponse({
                    'type'    : 'add',
                    'name'    : lang.name,
                    'href'    : reverse('exam:language-edit', args=[lang.pk]),
                    'success' : True,
                    'message' : '<strong>Language created!</strong> The new languages has successfully been created.',
                })
    
    
    form_html = render_crispy_form(language_form)
    return JsonResponse({
                'title'   : 'Add new language',
                'form'    : form_html,
                'submit'  : 'Create',
                'success' : False,
            })

@login_required
def edit_language(request, lang_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    delegation = Delegation.objects.get(members=request.user)
    
    instance = get_object_or_404(Language, pk=lang_id)
    language_form = LanguageForm(request.POST or None, instance=instance)
    if language_form.is_valid():
        lang = language_form.save()
        
        return JsonResponse({
                    'type'    : 'edit',
                    'name'    : lang.name,
                    'href'    : reverse('exam:language-edit', args=[lang.pk]),
                    'success' : True,
                    'message' : '<strong>Language modified!</strong> The language '+lang.name+' has successfully been modified.',
                })
    
    
    form_html = render_crispy_form(language_form)
    return JsonResponse({
                'title'   : 'Edit language',
                'form'    : form_html,
                'submit'  : 'Save',
                'success' : False,
            })


@login_required
@ensure_csrf_cookie
def figure_list(request):
    figure_list = Figure.objects.all()
    
    return render(request, 'ipho_exam/figures.html',
            {
                'figure_list' : figure_list,
            })

import re
figparam_placeholder = re.compile(r'%([\w-]+)%')

@login_required
def figure_add(request):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    
    form = FigureForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        # import codecs
        # f = codecs.open('unicode.rst', encoding='utf-8')
        obj.content = request.FILES['file'].read()
        placeholders = figparam_placeholder.findall(obj.content)
        obj.params = ','.join(placeholders)
        obj.save()
    
        return JsonResponse({
                    'type'      : 'add',
                    'name'      : obj.name,
                    'params'    : obj.params,
                    'src'       : reverse('exam:figure-export', args=[obj.pk]),
                    'edit-href' : reverse('exam:figure-edit', args=[obj.pk]),
                    'success'   : True,
                    'message'   : '<strong>Figure added!</strong> The new figure has successfully been created.',
                })
    
    form_html = render_crispy_form(form)
    return JsonResponse({
                'title'   : 'Add new figure',
                'form'    : form_html,
                'submit'  : 'Upload',
                'success' : False,
            })

@login_required
def figure_edit(request, fig_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    
    instance = get_object_or_404(Figure, pk=fig_id)
    form = FigureForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        obj = form.save()
        if 'file' in request.FILES:
            obj.content = request.FILES['file'].read()
            placeholders = figparam_placeholder.findall(obj.content)
            obj.params = ','.join(placeholders)
            obj.save()
        
        return JsonResponse({
                    'type'    : 'edit',
                    'name'      : obj.name,
                    'params'    : obj.params,
                    'src'       : reverse('exam:figure-export', args=[obj.pk]),
                    'edit-href' : reverse('exam:figure-edit', args=[obj.pk]),
                    'success'   : True,
                    'message' : '<strong>Figure modified!</strong> The figure '+obj.name+' has successfully been modified.',
                })
    
    
    form_html = render_crispy_form(form)
    return JsonResponse({
                'title'   : 'Edit figure',
                'form'    : form_html,
                'submit'  : 'Save',
                'success' : False,
            })

@login_required
def figure_export(request, fig_id, output_format='svg'):
    fig_svg = Figure.get_fig_query(fig_id, request.GET)
    if output_format == 'svg':
        return HttpResponse(fig_svg, content_type="image/svg+xml")
    if output_format == 'pdf':
        import cairosvg
        fig_pdf = cairosvg.svg2pdf(fig_svg.encode('utf8'))
        return HttpResponse(fig_pdf, content_type="application/pdf")


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
        exam = get_object_or_404(Exam, id=exam_id)
    if question_id is not None:
        question = get_object_or_404(Question, id=question_id)
    elif exam is not None and exam.question_set.count() > 0:
        question = exam.question_set.all()[0]
    
    delegation = Delegation.objects.filter(members=request.user)
    
    orig_lang = get_object_or_404(Language, id=orig_id)
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
            orig_node = get_object_or_404(TranslationNode, question=question, language=orig_lang)
        orig_q = qml.QMLquestion(orig_node.text)
        
        content_set = qml.make_content(orig_q)
        
        trans_content = {}
        if lang_id is not None:
            trans_lang = get_object_or_404(Language, id=lang_id)
            trans_node, created = TranslationNode.objects.get_or_create(question=question, language_id=lang_id, defaults={'text': '', 'status' : 'O'}) ## TODO: check permissions for this.
            if len(trans_node.text) > 0:
                trans_q    = qml.QMLquestion(trans_node.text)
                trans_content = trans_q.get_data()
            
            form = qml.QMLForm(orig_q, trans_content, request.POST or None)
        
            if form.is_valid():
                if trans_node.status == 'L':
                    raise Exception('The question cannot be modified. It is locked.')
                if trans_node.status == 'S':
                    raise Exception('The question cannot be modified. It is already submitted.')
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


@login_required
def pdf(request, question_id, lang_id, raw_tex=False):
    question = get_object_or_404(Question, id=question_id)
    
    trans_lang = get_object_or_404(Language, id=lang_id)
    if trans_lang.versioned:
        trans_node = VersionNode.objects.filter(question=question, language=trans_lang, status='C').order_by('-version')[0]
    else:
        trans_node = get_object_or_404(TranslationNode, question=question, language=trans_lang)
    
    trans_q = qml.QMLquestion(trans_node.text)
    trans_content, ext_resources = trans_q.make_tex()
    
    context = {
                'polyglossia' : trans_lang.polyglossia,
                'extraheader' : trans_lang.extraheader,
                'title'       : question.name,
                'document'    : trans_content,
                'filename'    : u'IPhO16 - {} Q{} - {}.pdf'.format(question.exam.name, question.position, trans_lang.name),
              }
    if raw_tex:
        return render(request, 'ipho_exam/tex/exam_question.tex', context, content_type='text/plain')
    return tex.render_tex(request, 'ipho_exam/tex/exam_question.tex', context, ext_resources)


