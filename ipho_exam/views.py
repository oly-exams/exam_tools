# coding=utf-8
from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404

from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.core.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string

from copy import deepcopy
from collections import OrderedDict

from tempfile import mkdtemp
import subprocess
import os
import shutil
from hashlib import md5


from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, Language, Figure, Feedback, StudentSubmission, ExamDelegationSubmission
from ipho_exam import qml, tex

from ipho_exam.forms import LanguageForm, FigureForm, TranslationForm, FeedbackForm, AdminBlockForm, AdminBlockAttributeFormSet, AdminBlockAttributeHelper, SubmissionAssignForm

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
@ensure_csrf_cookie
def list(request):
    delegation = Delegation.objects.filter(members=request.user)

    # if request.is_ajax and 'exam_id' in request.GET:
    if 'exam_id' in request.GET:
        exam = get_object_or_404(Exam, id=request.GET['exam_id'])
        node_list = TranslationNode.objects.filter(question__exam=exam, language__delegation=delegation)
        return render(request, 'ipho_exam/partials/list_exam_tbody.html',
                {
                    'exam'      : exam,
                    'node_list' : node_list,
                })
    else:
        exam_list = Exam.objects.filter(hidden=False)
        return render(request, 'ipho_exam/list.html',
                {
                    'exam_list' : exam_list,
                })

@login_required
def add_translation(request, exam_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    delegation = Delegation.objects.get(members=request.user)
    exam = get_object_or_404(Exam, id=exam_id)

    translation_form = TranslationForm(request.POST or None)
    translation_form.fields['question'].queryset = Question.objects.filter(exam=exam)
    translation_form.fields['language'].queryset = Language.objects.filter(delegation=delegation)
    if translation_form.is_valid():
        translation_form.cleaned_data['status'] = 'O'
        translation_form.data['status'] = 'O'
        translation_form.save()

        return JsonResponse({
                    'success' : True,
                    'message' : '<strong>Translation added!</strong> The new translation has successfully been added.',
                    'exam_id' : exam.pk,
                })


    form_html = render_crispy_form(translation_form)
    return JsonResponse({
                'title'       : 'Add translation to {}'.format(exam.name),
                'form'        : form_html,
                'submit_text' : 'Add',
                'success'     : False,
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
def feedbacks_list(request):
    exam_list = Exam.objects.filter(hidden=False, feedback_active=True)

    if 'exam_id' in request.GET:
        exam = get_object_or_404(Exam, id=request.GET['exam_id'], feedback_active=True)
        feedbacks = Feedback.objects.filter(question__exam=request.GET['exam_id']).order_by('-timestamp')
        return render(request, 'ipho_exam/partials/feedbacks_tbody.html',
                {
                    'feedbacks' : feedbacks,
                })
    else:
        return render(request, 'ipho_exam/feedbacks.html', {
                    'exam_list' : exam_list,
                })

@login_required
def feedbacks_add(request, exam_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    delegation = Delegation.objects.get(members=request.user)
    exam = get_object_or_404(Exam, id=exam_id, feedback_active=True)

    ## Language section
    form = FeedbackForm(request.POST or None)
    form.fields['question'].queryset = Question.objects.filter(exam=exam)
    if form.is_valid():
        form.instance.delegation = delegation
        form.save()

        return JsonResponse({
                    'success' : True,
                    'message' : '<strong>Feedback added!</strong> The new feedback has successfully been added. The staff will look at it.',
                    'exam_id' : exam.pk,
                })

    form_html = render_crispy_form(form)
    return JsonResponse({
                'title'   : 'Add new feedback',
                'form'    : form_html,
                'submit'  : 'Submit',
                'success' : False,
            })


@permission_required('iphoperm.is_staff')
@ensure_csrf_cookie
def figure_list(request):
    figure_list = Figure.objects.all()

    return render(request, 'ipho_exam/figures.html',
            {
                'figure_list' : figure_list,
            })

import re
figparam_placeholder = re.compile(r'%([\w-]+)%')

@permission_required('iphoperm.is_staff')
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

@permission_required('iphoperm.is_staff')
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


@permission_required('iphoperm.is_staff')
@ensure_csrf_cookie
def admin_list(request):
    if request.is_ajax and 'exam_id' in request.GET:
        exam = get_object_or_404(Exam, id=request.GET['exam_id'])
        return JsonResponse({
                    'sort_url' : reverse('exam:admin-sort', args=[exam.pk]),
                    'content'  : render_to_string('ipho_exam/partials/admin_exam_tbody.html', {'exam': exam}),
                })
    else:
        exam_list = Exam.objects.filter(hidden=False)
        return render(request, 'ipho_exam/admin.html',
                {
                    'exam_list' : exam_list,
                })
@permission_required('iphoperm.is_staff')
def admin_sort(request, exam_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    for position, question_id in enumerate(request.POST.getlist('ex{}_q[]'.format(exam_id))):
        question = get_object_or_404(Question, pk=int(question_id))
        question.position = position
        question.save()
    return HttpResponse('')
@permission_required('iphoperm.is_staff')
def admin_props(request, exam_id, question_id):
    pass


@permission_required('iphoperm.is_staff')
@ensure_csrf_cookie
def admin_editor(request, exam_id, question_id):
    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)

    lang = get_object_or_404(Language, id=lang_id)
    if lang.versioned:
        node = VersionNode.objects.filter(question=question, language=lang, status='C').order_by('-version')[0]
    else:
        node = get_object_or_404(TranslationNode, question=question, language=lang)

    q = qml.QMLquestion(node.text)
    #content_set = qml.make_content(q)

    context = {
        'exam' : exam,
        'question' : question,
        'content_set' : q.children,
    }
    return render(request, 'ipho_exam/admin_editor.html', context)

@permission_required('iphoperm.is_staff')
def admin_editor_block(request, exam_id, question_id, block_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)

    lang = get_object_or_404(Language, id=lang_id)
    if lang.versioned:
        node = VersionNode.objects.filter(question=question, language=lang).order_by('-version')[0]
    else:
        node = get_object_or_404(TranslationNode, question=question, language=lang)

    q = qml.QMLquestion(node.text)

    block = q.find(block_id)
    if block is None:
        raise Http404('block_id not found')

    heading = 'Edit '+block.heading() if block.heading() is not None else 'Edit block'

    form = AdminBlockForm(block, request.POST or None)
    attrs_form = AdminBlockAttributeFormSet(request.POST or None, initial=[{'key':k,'value':v} for k,v in block.attributes.items()])
    if form.is_valid() and attrs_form.is_valid():
        if 'block_content' in form.cleaned_data:
            block.data = form.cleaned_data['block_content']
            block.data_html = form.cleaned_data['block_content']
        block.attributes = dict([(ff.cleaned_data['key'],ff.cleaned_data['value']) for ff in attrs_form if ff.cleaned_data])
        node.text = qml.xml2string(q.make_xml())
        if lang.versioned: ## make new version and increase version number
            node.pk = None
            node.version += 1
            node.status = 'P'
        node.save()

        return JsonResponse({
                    'title'      : heading,
                    'content'    : block.content_html(),
                    'attributes' : render_to_string('ipho_exam/partials/admin_editor_attributes.html', {'attributes': block.attributes}),
                    'success'    : True,
                })

    form_html = render_crispy_form(form)
    attrs_form_html = render_crispy_form(attrs_form, AdminBlockAttributeHelper())
    return JsonResponse({
                'title'   : heading,
                'form'    : form_html+attrs_form_html,
                'success' : False,
            })

@permission_required('iphoperm.is_staff')
def admin_editor_add_block(request, exam_id, question_id, block_id, tag_name):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)

    lang = get_object_or_404(Language, id=lang_id)
    if lang.versioned:
        node = VersionNode.objects.filter(question=question, language=lang).order_by('-version')[0]
    else:
        node = get_object_or_404(TranslationNode, question=question, language=lang)

    q = qml.QMLquestion(node.text)

    block = q.find(block_id)
    if block is None:
        raise Http404('block_id not found')

    newblock = block.add_child(qml.ET.fromstring(u'<{} />'.format(tag_name)))
    node.text = qml.xml2string(q.make_xml())
    if lang.versioned: ## make new version and increase version number
        node.pk = None
        node.version += 1
        node.status = 'P'
    node.save()

    ctx = {
        'fields_set': [newblock],
        'exam': exam,
        'question': question,
    }
    return JsonResponse({
                'new_block' : render_to_string('ipho_exam/admin_editor_field.html', ctx),
                'success'    : True,
            })

@login_required
def submission_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    delegation = Delegation.objects.get(members=request.user)
    official_lang = Language.objects.get(id=OFFICIAL_LANGUAGE)
    languages = Language.objects.filter(delegation=delegation)

    ex_submission, _ = ExamDelegationSubmission.objects.get_or_create(exam=exam, delegation=delegation)

    if request.POST:
        print request.POST

    assigned_student_language = OrderedDict()
    for student in delegation.student_set.all():
        stud_langs = OrderedDict()
        for lang in [official_lang]:
            stud_langs[lang] = False
        for lang in languages:
            stud_langs[lang] = False
        assigned_student_language[student] = (stud_langs)

    student_languages = StudentSubmission.objects.filter(exam=exam, student__delegation=delegation)
    for sl in student_languages:
        assigned_student_language[sl.student][sl.language] = True

    return render(request, 'ipho_exam/submission.html', {
                'exam' : exam,
                'delegation' : delegation,
                'languages' : languages,
                'official_languages' : [official_lang],
                'submission_status' : ex_submission.status,
                'students_languages' : assigned_student_language,
            })

@login_required
def submission_exam_confirm(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    delegation = Delegation.objects.get(members=request.user)
    official_lang = Language.objects.get(id=OFFICIAL_LANGUAGE)
    languages = Language.objects.filter(delegation=delegation)

    ex_submission, _ = ExamDelegationSubmission.objects.get_or_create(exam=exam, delegation=delegation)

    if request.POST:
        print request.POST

    assigned_student_language = OrderedDict()
    for student in delegation.student_set.all():
        stud_langs = OrderedDict()
        for lang in [official_lang]:
            stud_langs[lang] = False
        for lang in languages:
            stud_langs[lang] = False
        assigned_student_language[student] = (stud_langs)

    student_languages = StudentSubmission.objects.filter(exam=exam, student__delegation=delegation)
    for sl in student_languages:
        assigned_student_language[sl.student][sl.language] = True

    return render(request, 'ipho_exam/submission_confirm.html', {
                'exam' : exam,
                'delegation' : delegation,
                'languages' : languages,
                'official_languages' : [official_lang],
                'submission_status' : ex_submission.status,
                'students_languages' : assigned_student_language,
            })


@permission_required('iphoperm.is_staff')
def admin_submission_list(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    delegation = Delegation.objects.get(members=request.user)
    submissions = StudentSubmission.objects.filter(exam=exam, student__delegation=delegation)

    return render(request, 'ipho_exam/admin_submissions.html', {
                'exam' : exam,
                'submissions' : submissions,
            })

@permission_required('iphoperm.is_staff')
def admin_submission_assign(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    delegation = Delegation.objects.get(members=request.user)

    if request.POST:
        form = SubmissionAssignForm(request.POST)
        if form.is_valid():
            form.instance.exam = exam
            form.save()
        return HttpResponseRedirect(reverse('exam:admin-submission-list', args=(exam.pk,)))
    else:
        form = SubmissionAssignForm()
        form.fields['student'].queryset = Student.objects.filter(delegation=delegation)
        form.fields['language'].queryset = Language.objects.filter(delegation=delegation) | Language.objects.filter(id=OFFICIAL_LANGUAGE)
        ## TODO: identify official languages by delegation

        ctx = RequestContext(request)
        ctx.update(csrf(request))
        return HttpResponse(render_crispy_form(form, context=ctx))

@permission_required('iphoperm.is_staff')
def admin_submission_delete(request, submission_id):
    pass


@login_required
def editor(request, exam_id=None, question_id=None, lang_id=None, orig_id=OFFICIAL_LANGUAGE, orig_diff=None):
    context = {'exam_id'     : exam_id,
               'question_id' : question_id,
               'lang_id'     : question_id,
               'orig_id'     : orig_id,
               'orig_diff'   : orig_diff,
               }
    exam_list = Exam.objects.filter(hidden=False) # TODO: allow admin to see all exams
    context['exam_list'] = exam_list

    exam = None
    question = None
    question_langs = None
    own_lang = None
    question_versions = None
    content_set = None
    form = None
    trans_extra_html = None
    orig_lang = None
    trans_lang = None

    if exam_id is not None:
        exam = get_object_or_404(Exam, id=exam_id)
    if question_id is not None:
        question = get_object_or_404(Question, id=question_id)
    elif exam is not None and exam.question_set.count() > 0:
        question = exam.question_set.all()[0]

    delegation = Delegation.objects.filter(members=request.user)


    ## TODO:
    ## * check for read-only questions
    ## * deal with errors when node not found: no content

    if question:
        orig_lang = get_object_or_404(Language, id=orig_id)

        if delegation.count() > 0:
            own_lang = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
        elif request.user.is_superuser:
            own_lang = Language.objects.all().order_by('name')


    # try:
        ## TODO: make a free function
        if orig_lang.versioned:
            orig_node = VersionNode.objects.filter(question=question, language=orig_lang, status='C').order_by('-version')[0]
            orig_lang.version = orig_node.version
            question_versions = VersionNode.objects.values_list('version', flat=True).order_by('-version').filter(question=question, language=orig_lang, status='C')[1:]
        else:
            orig_node = get_object_or_404(TranslationNode, question=question, language=orig_lang)


        question_langs = []
        ## TODO: improve this loop. maybe with annotate?
        for vn in VersionNode.objects.filter(question=question, status='C').order_by('-version'):
            if not vn.language in question_langs:
                question_langs.append(vn.language)
                question_langs[-1].version = vn.version
        question_langs += Language.objects.filter(translationnode__question=question)


        orig_q = qml.QMLquestion(orig_node.text)

        if orig_diff is not None:
            if not orig_lang.versioned:
                raise Exception('Original language does not support versioning.')
            orig_diff_node = get_object_or_404(VersionNode, question=question, language=orig_lang, version=orig_diff)
            orig_diff_q = qml.QMLquestion(orig_diff_node.text)
            orig_diff_data = orig_diff_q.get_data()

            ## make diff
            ## show diff, new elements
            ## don't show, removed elements (non-trivial insert in the tree)
            orig_q.diff_content_html(orig_diff_data)

        content_set = qml.make_content(orig_q)


        trans_content = {}
        if lang_id is not None:
            trans_lang = get_object_or_404(Language, id=lang_id)
            trans_node, created = TranslationNode.objects.get_or_create(question=question, language_id=lang_id, defaults={'text': '', 'status' : 'O'}) ## TODO: check permissions for this.
            if len(trans_node.text) > 0:
                trans_q    = qml.QMLquestion(trans_node.text)
                trans_content = trans_q.get_data()
                trans_extra_html = trans_q.get_trans_extra_html()

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
    if context['orig_diff'] is not None: context['orig_diff'] = int(context['orig_diff'])
    context['exam']          = exam
    context['question']      = question
    context['question_langs'] = question_langs
    context['question_versions'] = question_versions
    context['own_lang']         = own_lang
    context['orig_lang']        = orig_lang
    context['trans_lang']       = trans_lang
    context['content_set']      = content_set
    context['form']             = form
    context['trans_extra_html'] = trans_extra_html
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
