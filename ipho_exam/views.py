# coding=utf-8
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotModified, JsonResponse, Http404, HttpResponseForbidden
from django.http.request import QueryDict

from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string
from django.db.models import Q, Count, Sum, Case, When, IntegerField

from copy import deepcopy
from collections import OrderedDict
from django.utils import timezone
from tempfile import mkdtemp
from hashlib import md5
import itertools

from django.conf import settings
from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, PDFNode, Language, Figure, Feedback, Like, StudentSubmission, ExamAction, TranslationImportTmp, Document, DocumentTask
from ipho_exam import qml, tex, pdf, iphocode, qquery, fonts, cached_responses, question_utils

from ipho_exam.forms import LanguageForm, FigureForm, TranslationForm, PDFNodeForm, FeedbackForm, AdminBlockForm, AdminBlockAttributeFormSet, AdminBlockAttributeHelper, SubmissionAssignForm, AssignTranslationForm, TranslationImportForm, AdminImportForm

import ipho_exam
from ipho_exam import tasks
import celery
from celery.result import AsyncResult

OFFICIAL_LANGUAGE = 1
OFFICIAL_DELEGATION = getattr(settings, 'OFFICIAL_DELEGATION')

@login_required
def index(request):
    return render(request, 'ipho_exam/index.html')

@login_required
@ensure_csrf_cookie
def main(request):
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
    exams_open = ExamAction.objects.filter(delegation=delegation, exam=exam_list, exam__active=True,
        action=ExamAction.TRANSLATION, status=ExamAction.OPEN).values('exam__pk','exam__name')
    exams_closed = ExamAction.objects.filter(delegation=delegation, exam=exam_list,
        action=ExamAction.TRANSLATION, status=ExamAction.SUBMITTED).values('exam__pk','exam__name')
    return render(request, 'ipho_exam/main.html',
            {
                'own_lang'      : own_lang,
                'other_lang'    : other_lang,
                'exam_list'     : exam_list,
                'exams_open'    : exams_open,
                'exams_closed'  : exams_closed,
                'success'       : success,
            })

def time_response(request):
    return HttpResponse(timezone.now().isoformat(), content_type="text/plain")

@login_required
def wizard(request):
    delegation = Delegation.objects.filter(members=request.user)

    own_languages = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
    ## Exam section
    exam_list = Exam.objects.filter(hidden=False)
    open_submissions = ExamAction.objects.filter(exam=exam_list, exam__active=True,
     delegation=delegation, action=ExamAction.TRANSLATION, status=ExamAction.OPEN)
    closed_submissions = ExamAction.objects.filter(exam=exam_list, delegation=delegation, action=ExamAction.TRANSLATION, status=ExamAction.SUBMITTED)
    # Translations
    translations = TranslationNode.objects.filter(language=own_languages, question__exam=exam_list)


    return render(request, 'ipho_exam/wizard.html',
            {
                'own_languages' : own_languages,
                'exam_list'     : exam_list,
                'exams_open'    : open_submissions,
                'exams_closed'  : closed_submissions,
                'translations'  : translations,
            })

@login_required
@ensure_csrf_cookie
def translations_list(request):
    delegation = Delegation.objects.filter(members=request.user)

    # if request.is_ajax and 'exam_id' in request.GET:
    if 'exam_id' in request.GET:
        exam = get_object_or_404(Exam, id=request.GET['exam_id'])
        trans_list = TranslationNode.objects.filter(question__exam=exam, language__delegation=delegation).order_by('language', 'question')
        pdf_list = PDFNode.objects.filter(question__exam=exam, language__delegation=delegation).order_by('language', 'question')
        node_list = list(trans_list) + list(pdf_list)
        official_translations = VersionNode.objects.filter(question__exam=exam, language__delegation__name=OFFICIAL_DELEGATION, status='C').order_by('-version')
        official_nodes = []
        qdone = set()
        for node in official_translations:
            if node.question not in qdone:
                official_nodes.append(node)
                qdone.add(node.question)
        return render(request, 'ipho_exam/partials/list_exam_tbody.html',
                {
                    'exam'      : exam,
                    'node_list' : node_list,
                    'official_nodes': official_nodes,
                })
    else:
        exam_list = Exam.objects.filter(hidden=False)
        return render(request, 'ipho_exam/list.html',
                {
                    'exam_list' : exam_list,
                })

@login_required
@ensure_csrf_cookie
def list_all_translations(request):
    exams = Exam.objects.filter(hidden=False)
    delegations = Delegation.objects.all()

    def get_or_none(model, *args, **kwargs):
        try:
            return model.objects.get(*args, **kwargs)
        except model.DoesNotExist:
            return None

    filter_ex = exams
    exam = get_or_none(Exam, id=request.GET.get('ex', None))
    if exam is not None:
        filter_ex = exam
    filter_dg = delegations
    delegation = get_or_none(Delegation, id=request.GET.get('dg', None))
    if delegation is not None:
        filter_dg = delegation

    trans_list = TranslationNode.objects.filter(question__exam=filter_ex, language__delegation=filter_dg).order_by('language__delegation', 'question')
    pdf_list = PDFNode.objects.filter(question__exam=filter_ex, language__delegation=filter_dg).order_by('language__delegation', 'question')
    all_nodes = list(trans_list) + list(pdf_list)

    paginator = Paginator(all_nodes, 25) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        node_list = paginator.page(page)
    except PageNotAnInteger:
        node_list = paginator.page(1)
    except EmptyPage:
        node_list = paginator.page(paginator.num_pages)

    class url_builder(object):
        def __init__(self, base_url, get={}):
            self.url = base_url
            self.get = get
        def __call__(self, **kwargs):
            qdict = QueryDict('', mutable=True)
            for k,v in self.get.iteritems():
                qdict[k] = v
            for k,v in kwargs.iteritems():
                if v is None:
                    if k in qdict: del qdict[k]
                else:
                    qdict[k] = v
            url = self.url + '?' + qdict.urlencode()
            return url

    return render(request, 'ipho_exam/list_all.html',
            {
                'exams'       : exams,
                'exam'        : exam,
                'delegations' : delegations,
                'delegation'  : delegation,
                'node_list'   : node_list,
                'all_pages'   : range(1,paginator.num_pages+1),
                'this_url_builder'    : url_builder(reverse('exam:list-all'), request.GET),
            })


@login_required
def add_translation(request, exam_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    delegation = Delegation.objects.get(members=request.user)
    exam = get_object_or_404(Exam, id=exam_id)

    translation_form = TranslationForm(request.POST or None)
    translation_form.fields['language'].queryset = Language.objects.filter(delegation=delegation).exclude(translationnode__question__exam=exam).exclude(pdfnode__question__exam=exam) # TODO: still allow for languages that are not created for all questions
    if translation_form.is_valid():
        for question in exam.question_set.exclude(translationnode__language=translation_form.cleaned_data['language']):
            if translation_form.cleaned_data['language'].is_pdf:
                node = PDFNode(language=translation_form.cleaned_data['language'], question=question, status='O')
                node.save()
            else:
                node = TranslationNode(language=translation_form.cleaned_data['language'], question=question, status='O')
                node.save()

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
def add_pdf_node(request, question_id, lang_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    delegation = Delegation.objects.get(members=request.user)
    question = get_object_or_404(Question, id=question_id)
    lang = get_object_or_404(Language, id=lang_id)
    ## TODO: check permissions

    node = get_object_or_404(PDFNode, question=question, language=lang)
    ## Language section
    node_form = PDFNodeForm(request.POST or None, request.FILES or None, instance=node)
    if node_form.is_valid():
        node_form.save()

        return JsonResponse({
                    'success' : True,
                    'message' : '<strong>PDF uploaded!</strong> The translation of {} in <emph>{}</emph> has been updated.'.format(question.name, lang.name),
                })


    form_html = render_crispy_form(node_form)
    return JsonResponse({
                'title'   : 'Upload new version',
                'form'    : form_html,
                'submit'  : 'Upload',
                'success' : False,
            })

@login_required
def translation_export(request, question_id, lang_id, version_num=None):
    if version_num is None:
        trans = qquery.latest_version(question_id, lang_id)
    else:
        trans = qquery.get_version(question_id, lang_id, version_num)

    content = qml.xml2string(trans.qml.make_xml())
    content = qml.unescape_entities(content)

    res = HttpResponse(content, content_type="application/ipho+qml+xml")
    res['content-disposition'] = 'attachment; filename="{}"'.format('iphoexport_q{}_l{}.xml'.format(question_id, lang_id))
    return res
@login_required
def translation_import(request, question_id, lang_id):
    delegation = Delegation.objects.get(members=request.user)
    language = get_object_or_404(Language, id=lang_id)
    question = get_object_or_404(Question, id=question_id)
    if not language.check_permission(request.user):
        return HttpResponseForbidden('You do not have the permissions to edit this language.')

    form = TranslationImportForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        txt = request.FILES['file'].read()
        txt = txt.decode('utf8')
        obj.content = qml.escape_equations(txt)
        obj.question = question
        obj.language = language
        obj.save()
        return HttpResponseRedirect(reverse('exam:import-translation-confirm', args=(str(obj.slug),)))

    form_html = render_crispy_form(form)
    return JsonResponse({
                'title'   : 'Import question',
                'form'    : form_html,
                'submit'  : 'Upload',
                'success' : False,
            })
@login_required
@csrf_protect
def translation_import_confirm(request, slug):
    trans_import = get_object_or_404(TranslationImportTmp, slug=slug)
    trans = qquery.latest_version(trans_import.question.pk, trans_import.language.pk)

    if request.POST:
        trans.node.text = trans_import.content
        trans.node.save()
        trans_import.delete()

        return JsonResponse({
                    'success' : True,
                    'message' : '<strong>Question imported!</strong> The translation of {} in <emph>{}</emph> has been updated.'.format(trans.question.name, trans.lang.name),
                })

    old_q = trans.qml
    old_data = old_q.get_data()
    new_q = qml.QMLquestion(trans_import.content)
    new_data = new_q.get_data()

    old_q.diff_content_html(new_data)
    new_q.diff_content_html(old_data)

    old_flat_dict = old_q.flat_content_dict()

    ctx = RequestContext(request)
    ctx.update(csrf(request))
    ctx['fields_set'] = [new_q]
    ctx['old_content'] = old_flat_dict
    form_html = render_to_string('ipho_exam/partials/qml_diff.html', ctx),
    return JsonResponse({
                'title'   : 'Review the changes before accepting the new version',
                'form'    : form_html,
                'submit'  : 'Confirm',
                'href'    : reverse('exam:import-translation-confirm', args=(slug,)),
                'success' : False,
            })


@login_required
@ensure_csrf_cookie
def list_language(request):
    delegation = Delegation.objects.filter(members=request.user)
    languages = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
    return render(request, 'ipho_exam/languages.html', {'languages': languages})

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

        languages = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
        return JsonResponse({
                    'type'    : 'add',
                    'name'    : lang.name,
                    'href'    : reverse('exam:language-edit', args=[lang.pk]),
                    'tbody'   : render_to_string('ipho_exam/partials/languages_tbody.html', {'languages': languages}),
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

        languages = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
        return JsonResponse({
                    'type'    : 'edit',
                    'name'    : lang.name,
                    'href'    : reverse('exam:language-edit', args=[lang.pk]),
                    'tbody'   : render_to_string('ipho_exam/partials/languages_tbody.html', {'languages': languages}),
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
    delegation = Delegation.objects.get(members=request.user)

    if 'exam_id' in request.GET:
        exam = get_object_or_404(Exam, id=request.GET['exam_id'], feedback_active=True)
        feedbacks = Feedback.objects.filter(
            question__exam=request.GET['exam_id']
        ).annotate(
             num_likes=Sum(
                 Case(When(like__status='L', then=1),
                      output_field=IntegerField())
             ),
             num_unlikes=Sum(
                 Case(When(like__status='U', then=1),
                      output_field=IntegerField())
             ),
             delegation_likes=Sum(
                Case(
                    When(like__delegation=delegation, then=1),
                    output_field=IntegerField()
                )
             )
        ).values(
            'num_likes',
            'num_unlikes',
            'delegation_likes',
            'pk',
            'question__name',
            'delegation__name',
            'delegation__country',
            'status',
            'timestamp',
            'part',
            'comment'
        ).order_by('-timestamp')
        choices = dict(Feedback._meta.get_field_by_name('status')[0].flatchoices)
        for fb in feedbacks:
            fb['status_display'] = choices[fb['status']]
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

@login_required
def feedback_like(request, status, feedback_id):
    feedback = get_object_or_404(Feedback, pk=feedback_id, question__exam__feedback_active=True)
    delegation = Delegation.objects.get(members=request.user)
    Like.objects.get_or_create(feedback=feedback, delegation=delegation, defaults={'status': status})
    return redirect('exam:feedbacks-list')


@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def figure_list(request):
    figure_list = Figure.objects.all()

    return render(request, 'ipho_exam/figures.html',
            {
                'figure_list' : figure_list,
            })

import re
figparam_placeholder = re.compile(r'%([\w-]+)%')

@permission_required('ipho_core.is_staff')
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
                    'figid'     : obj.pk,
                    'name'      : obj.name,
                    'params'    : obj.params,
                    'src'       : reverse('exam:figure-export', args=[obj.pk]),
                    'edit-href' : reverse('exam:figure-edit', args=[obj.pk]),
                    'delete-href' : reverse('exam:figure-delete', args=[obj.pk]),
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

@permission_required('ipho_core.is_staff')
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
                    'figid'     : obj.pk,
                    'name'      : obj.name,
                    'params'    : obj.params,
                    'src'       : reverse('exam:figure-export', args=[obj.pk]),
                    'edit-href' : reverse('exam:figure-edit', args=[obj.pk]),
                    'delete-href' : reverse('exam:figure-delete', args=[obj.pk]),
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
@permission_required('ipho_core.is_staff')
def figure_delete(request, fig_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    obj = get_object_or_404(Figure, pk=fig_id)
    obj.delete()
    return JsonResponse({
                'success' : True,
            })


@login_required
def figure_export(request, fig_id, output_format='svg', lang_id=None):
    lang = get_object_or_404(Language, pk=lang_id) if lang_id is not None else None
    fig_svg = Figure.get_fig_query(fig_id, request.GET, lang)
    if output_format == 'svg':
        return HttpResponse(fig_svg, content_type="image/svg+xml")
    if output_format == 'pdf':
        tmpdir = mkdtemp()
        tmpfile = tmpdir+'/fig.pdf'
        Figure.to_pdf(fig_svg, tmpfile)
        return HttpResponse(open(tmpfile), content_type="application/pdf")


@permission_required('ipho_core.is_staff')
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
@permission_required('ipho_core.is_staff')
def admin_sort(request, exam_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    for position, question_id in enumerate(request.POST.getlist('ex{}_q[]'.format(exam_id))):
        question = get_object_or_404(Question, pk=int(question_id))
        question.position = position
        question.save()
    return HttpResponse('')

@permission_required('ipho_core.is_staff')
def admin_new_version(request, exam_id, question_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)

    lang = get_object_or_404(Language, id=lang_id)
    if lang.versioned:
        if VersionNode.objects.filter(question=question, language=lang).count() > 0:
            node = VersionNode.objects.filter(question=question, language=lang).order_by('-version')[0]
        else:
            node = VersionNode(question=question, language=lang, version=0, text='<question id="q0" />'.format(question.pk))
    else:
        node = get_object_or_404(TranslationNode, question=question, language=lang)

    if lang.versioned: ## make new version and increase version number
        node.pk = None
        node.version += 1
        node.status = 'P'
    node.save()

    return JsonResponse({'success' : True})

@permission_required('ipho_core.is_staff')
def admin_import_version(request, question_id):
    language = get_object_or_404(Language, id=OFFICIAL_LANGUAGE)
    question = get_object_or_404(Question, id=question_id)

    form = AdminImportForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        txt = request.FILES['file'].read()
        txt = txt.decode('utf8')
        if language.versioned:
            if VersionNode.objects.filter(question=question, language=language).exists():
                node = VersionNode.objects.filter(question=question, language=language).order_by('-version')[0]
            else:
                node = VersionNode(question=question, language=language, version=0,
                                   text='<question id="q0" />'.format(question.pk))
        else:
            node = get_object_or_404(TranslationNode, question=question, language=language)

        if language.versioned:  ## make new version and increase version number
            node.pk = None
            node.version += 1
            node.status = 'P'
        node.content = qml.escape_equations(txt)
        node.save()
        return JsonResponse({'success': True})

    form_html = render_crispy_form(form)
    return JsonResponse({
                'title'   : 'Import question',
                'form'    : form_html,
                'submit'  : 'Upload',
                'success' : False,
            })


@permission_required('ipho_core.is_staff')
def admin_accept_version(request, exam_id, question_id, version_num, compare_version=None):
    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)

    lang = get_object_or_404(Language, id=lang_id)

    if compare_version is None:
        compare_node = VersionNode.objects.filter(question=question, language=lang, status='C').order_by('-version')[0]
        return HttpResponseRedirect(reverse('exam:admin-accept-version-diff',
                                    kwargs=dict( exam_id=exam.pk, question_id=question.pk, version_num=int(version_num),
                                                 compare_version=compare_node.version)))

    if lang.versioned:
        node = get_object_or_404(VersionNode, question=question, language=lang, status='P', version=version_num)
        compare_node = get_object_or_404(VersionNode, question=question, language=lang, status='C', version=compare_version)
    else:
        ## TODO: add status check
        node = get_object_or_404(TranslationNode, question=question, language=lang)
        compare_node = get_object_or_404(TranslationNode, question=question, language=lang)

    ## Save and redirect
    if request.POST:
        node.status = 'C'
        node.save()
        return HttpResponseRedirect(reverse('exam:admin'))

    node_versions = []
    if lang.versioned:
        node_versions = VersionNode.objects.filter(question=question, language=lang, status='C').order_by('-version').values_list('version', flat=True)

    old_q = qml.QMLquestion(compare_node.text)
    old_data = old_q.get_data()
    new_q = qml.QMLquestion(node.text)
    new_data = new_q.get_data()

    old_q.diff_content_html(new_data)
    new_q.diff_content_html(old_data)

    old_flat_dict = old_q.flat_content_dict()

    ctx = {}
    ctx['exam'] = exam
    ctx['question'] = question
    ctx['lang'] = lang
    ctx['node'] = node
    ctx['compare_node'] = compare_node
    ctx['node_versions'] = node_versions
    ctx['fields_set'] = [new_q]
    ctx['old_content'] = old_flat_dict
    return render(request, 'ipho_exam/admin_accept_version.html', ctx)

    # node, compare_node, node_versions, exam, question, lang
    pass

@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def admin_editor(request, exam_id, question_id, version_num):
    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)

    lang = get_object_or_404(Language, id=lang_id)
    if lang.versioned:
        node = get_object_or_404(VersionNode, question=question, language=lang, version=version_num)
        node_version = node.version
        if node.status != 'P':
            raise RuntimeError('Can only edit questions with `Proposal` status.')
    else:
        node = get_object_or_404(TranslationNode, question=question, language=lang)
        node_version = 0

    q = qml.QMLquestion(node.text)
    #content_set = qml.make_content(q)

    qml_types = [(qobj.tag, qml.canonical_name(qobj)) for qobj in qml.QMLobject.all_objects()]
    context = {
        'exam' : exam,
        'question' : question,
        'content_set' : [q],
        'node_version' : node_version,
        'qml_types' : qml_types,
    }
    return render(request, 'ipho_exam/admin_editor.html', context)

@permission_required('ipho_core.is_staff')
def admin_editor_block(request, exam_id, question_id, version_num, block_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)

    lang = get_object_or_404(Language, id=lang_id)
    if lang.versioned:
        node = get_object_or_404(VersionNode, question=question, language=lang, version=version_num)
        if node.status != 'P':
            raise RuntimeError('Can only edit questions with `Proposal` status.')
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

@permission_required('ipho_core.is_staff')
def admin_editor_delete_block(request, exam_id, question_id, version_num, block_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)

    lang = get_object_or_404(Language, id=lang_id)
    if lang.versioned:
        node = get_object_or_404(VersionNode, question=question, language=lang, version=version_num)
        if node.status != 'P':
            raise RuntimeError('Can only edit questions with `Proposal` status.')
    else:
        node = get_object_or_404(TranslationNode, question=question, language=lang)

    q = qml.QMLquestion(node.text)

    block = q.delete(block_id)
    node.text = qml.xml2string(q.make_xml())
    node.save()

    return JsonResponse({
                'success' : True,
            })

@permission_required('ipho_core.is_staff')
def admin_editor_add_block(request, exam_id, question_id, version_num, block_id, tag_name):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)

    lang = get_object_or_404(Language, id=lang_id)
    if lang.versioned:
        node = get_object_or_404(VersionNode, question=question, language=lang, version=version_num)
        node_version = node.version
    else:
        node = get_object_or_404(TranslationNode, question=question, language=lang)
        node_version = 0

    q = qml.QMLquestion(node.text)

    block = q.find(block_id)
    if block is None:
        raise Http404('block_id not found')

    newblock = block.add_child(qml.ET.fromstring(u'<{} />'.format(tag_name)))
    node.text = qml.xml2string(q.make_xml())
    node.save()

    qml_types = [(qobj.tag, qml.canonical_name(qobj)) for qobj in qml.QMLobject.all_objects()]
    ctx = {
        'fields_set': [newblock],
        'exam': exam,
        'node_version': node_version,
        'question': question,
        'qml_types' : qml_types,
    }
    return JsonResponse({
                'new_block' : render_to_string('ipho_exam/admin_editor_field.html', ctx),
                'success'    : True,
            })


@login_required
def submission_exam_list(request):
    delegation = Delegation.objects.filter(members=request.user)

    ## Exam section
    exam_list = Exam.objects.filter(hidden=False) # TODO: allow admin to see all exams
    pk_exams_open = ExamAction.objects.filter(delegation=delegation, exam=exam_list, exam__active=True,
        action=ExamAction.TRANSLATION, status=ExamAction.OPEN).values_list('exam', flat=True)
    pk_exams_closed = ExamAction.objects.filter(delegation=delegation, exam=exam_list,
        action=ExamAction.TRANSLATION, status=ExamAction.SUBMITTED).values_list('exam', flat=True)
    exams_open = Exam.objects.filter(pk=pk_exams_open)
    exams_closed = Exam.objects.filter(pk=pk_exams_closed)

    return render(request, 'ipho_exam/submission_list.html', {'exams_open': exams_open, 'exams_closed': exams_closed})

@login_required
def submission_exam_assign(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    delegation = Delegation.objects.get(members=request.user)
    languages = Language.objects.annotate(num_questions=Count('translationnode__question'), num_pdf_questions=Count('pdfnode__question')).filter(  Q(delegation__name=OFFICIAL_DELEGATION) | (Q(delegation=delegation) & Q(num_questions=exam.question_set.count())) | (Q(delegation=delegation) & Q(num_pdf_questions=exam.question_set.count())) )

    ex_submission,_ = ExamAction.objects.get_or_create(exam=exam, delegation=delegation, action=ExamAction.TRANSLATION)
    if ex_submission.status == ExamAction.SUBMITTED and not settings.DEMO_MODE:
        return HttpResponseRedirect(reverse('exam:submission-exam-submitted', args=(exam.pk,)))

    submission_forms = []
    all_valid = True
    with_errors = False
    for stud in delegation.student_set.all():
        stud_langs = StudentSubmission.objects.filter(student=stud, exam=exam).values_list('language', flat=True)
        try:
            stud_main_lang_obj = StudentSubmission.objects.get(student=stud, exam=exam, with_answer=True)
            stud_main_lang = stud_main_lang_obj.language
        except StudentSubmission.DoesNotExist:
            stud_main_lang = None
        form = AssignTranslationForm(request.POST or None, prefix='stud-{}'.format(stud.pk),
                                     languages_queryset=languages,
                                     initial=dict(languages=stud_langs, main_language=stud_main_lang))
        all_valid = all_valid and form.is_valid()
        with_errors = with_errors or form.errors
        submission_forms.append( (stud, form) )

    if all_valid:
        ## Save form
        for stud, form in submission_forms:
            current_langs = []
            ## Modify the with_answer status and delete unused submissions
            for ss in StudentSubmission.objects.filter(student=stud, exam=exam):
                if ss.language in form.cleaned_data['languages']:
                    ss.with_answer = (form.cleaned_data['main_language'] == ss.language)
                    ss.save()
                    current_langs.append(ss.language)
                else:
                    ss.delete()
            ## Insert new submissions
            for lang in form.cleaned_data['languages']:
                if lang in current_langs: continue
                with_answer = (form.cleaned_data['main_language'] == lang)
                ss = StudentSubmission(student=stud, exam=exam, language=lang, with_answer=with_answer)
                ss.save()

        ## Generate PDF compilation
        for student in delegation.student_set.all():
            all_tasks = []
            student_languages = StudentSubmission.objects.filter(exam=exam, student=student)
            questions = exam.question_set.all()
            grouped_questions = {k: list(g) for k,g in itertools.groupby(questions, key=lambda q: q.position) }
            for position, qgroup in grouped_questions.iteritems():
                doc,_ = Document.objects.get_or_create(exam=exam, student=student, position=position)
                cover_ctx = {'student': student, 'exam': exam, 'question': qgroup[0]}
                question_task = question_utils.compile_stud_exam_question(qgroup, student_languages, cover=cover_ctx, commit=True)
                question_task.freeze()
                doc_task,_ = DocumentTask.objects.update_or_create(document=doc, defaults={'task_id':question_task.id})
                question_task.delay()

        ## Return
        return HttpResponseRedirect(reverse('exam:submission-exam-confirm', args=(exam.pk,)))

    empty_languages = Language.objects.filter(delegation=delegation).annotate(num_questions=Count('translationnode__question'),num_pdf_questions=Count('pdfnode__question')).exclude( Q(num_questions=exam.question_set.count()) | Q(num_pdf_questions=exam.question_set.count()) )

    return render(request, 'ipho_exam/submission_assign.html', {
                'exam' : exam,
                'delegation' : delegation,
                'languages' : languages,
                'empty_languages': empty_languages,
                'submission_forms' : submission_forms,
                'with_errors': with_errors,
            })

@login_required
def submission_exam_confirm(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    delegation = Delegation.objects.get(members=request.user)
    languages = Language.objects.annotate(num_questions=Count('translationnode__question'), num_pdf_questions=Count('pdfnode__question')).filter(  Q(delegation__name=OFFICIAL_DELEGATION) | (Q(delegation=delegation) & Q(num_questions=exam.question_set.count())) | (Q(delegation=delegation) & Q(num_pdf_questions=exam.question_set.count())) )
    form_error = ''

    ex_submission,_ = ExamAction.objects.get_or_create(exam=exam, delegation=delegation, action=ExamAction.TRANSLATION)
    if ex_submission.status == ExamAction.SUBMITTED and not settings.DEMO_MODE:
        return HttpResponseRedirect(reverse('exam:submission-exam-submitted', args=(exam.pk,)))

    documents = Document.objects.filter(exam=exam, student__delegation=delegation).order_by('student','position')
    all_finished = all([ not hasattr(doc, 'documenttask') for doc in documents ])

    if request.POST and all_finished:
        if 'agree-submit' in request.POST:
            ex_submission.status = ExamAction.SUBMITTED
            ex_submission.save()
            return HttpResponseRedirect(reverse('exam:submission-exam-submitted', args=(exam.pk,)))
        else:
            form_error = '<strong>Error:</strong> You have to agree on the final submission before continuing.'

    stud_documents = {k:list(g) for k,g in itertools.groupby(documents, key=lambda d: d.student.pk)}

    assigned_student_language = OrderedDict()
    for student in delegation.student_set.all():
        stud_langs = OrderedDict()
        for lang in languages:
            stud_langs[lang] = False
        assigned_student_language[student] = (stud_langs)

    student_languages = StudentSubmission.objects.filter(exam=exam, student__delegation=delegation)
    for sl in student_languages:
        if sl.with_answer:
            assigned_student_language[sl.student][sl.language] = 'A'
        else:
            assigned_student_language[sl.student][sl.language] = 'Q'

    return render(request, 'ipho_exam/submission_confirm.html', {
                'exam' : exam,
                'delegation' : delegation,
                'languages' : languages,
                'stud_documents': stud_documents,
                'all_finished': all_finished,
                'submission_status' : ex_submission.status,
                'students_languages' : assigned_student_language,
                'form_error' : form_error,
            })

@login_required
def submission_exam_submitted(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    delegation = Delegation.objects.get(members=request.user)
    languages = Language.objects.annotate(num_questions=Count('translationnode__question'), num_pdf_questions=Count('pdfnode__question')).filter(  Q(delegation__name=OFFICIAL_DELEGATION) | (Q(delegation=delegation) & Q(num_questions=exam.question_set.count())) | (Q(delegation=delegation) & Q(num_pdf_questions=exam.question_set.count())) )

    ex_submission,_ = ExamAction.objects.get_or_create(exam=exam, delegation=delegation, action=ExamAction.TRANSLATION)

    assigned_student_language = OrderedDict()
    for student in delegation.student_set.all():
        stud_langs = OrderedDict()
        for lang in languages:
            stud_langs[lang] = False
        assigned_student_language[student] = (stud_langs)

    student_languages = StudentSubmission.objects.filter(exam=exam, student__delegation=delegation)
    for sl in student_languages:
        if sl.with_answer:
            assigned_student_language[sl.student][sl.language] = 'A'
        else:
            assigned_student_language[sl.student][sl.language] = 'Q'

    documents = Document.objects.filter(exam=exam, student__delegation=delegation).order_by('student','position')
    stud_documents = {k:list(g) for k,g in itertools.groupby(documents, key=lambda d: d.student.pk)}

    return render(request, 'ipho_exam/submission_submitted.html', {
                'exam' : exam,
                'delegation' : delegation,
                'languages' : languages,
                'stud_documents': stud_documents,
                'submission_status' : ex_submission.status,
                'students_languages' : assigned_student_language,
            })


@permission_required('ipho_core.is_staff')
def admin_submission_list(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    delegation = Delegation.objects.get(members=request.user)
    submissions = StudentSubmission.objects.filter(exam=exam, student__delegation=delegation)

    return render(request, 'ipho_exam/admin_submissions.html', {
                'exam' : exam,
                'submissions' : submissions,
            })

@permission_required('ipho_core.is_staff')
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
        form.fields['language'].queryset = Language.objects.all()

        ctx = RequestContext(request)
        ctx.update(csrf(request))
        return HttpResponse(render_crispy_form(form, context=ctx))

@permission_required('ipho_core.is_staff')
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
    last_saved = None

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
        ## officials
        official_list = []
        for vn in VersionNode.objects.filter(question=question, status='C', language__delegation__name=OFFICIAL_DELEGATION).order_by('-version'):
            if not vn.language in official_list:
                official_list.append(vn.language)
                official_list[-1].version = vn.version
        # official_list += list(Language.objects.filter(translationnode__question=question, delegation__name=OFFICIAL_DELEGATION))
        question_langs.append({'name': 'official', 'order':0, 'list': official_list})
        ## own
        if delegation.count() > 0:
            question_langs.append({'name': 'own', 'order':1,
                'list':  Language.objects.filter(translationnode__question=question, delegation=delegation)
                })
        ## others
        question_langs.append({'name': 'others', 'order':2,
            'list': Language.objects.filter(translationnode__question=question).exclude(delegation=delegation).exclude(delegation__name=OFFICIAL_DELEGATION)
            })

        orig_q = qml.QMLquestion(orig_node.text)
        orig_q.set_lang(orig_lang)

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
                trans_q.set_lang(trans_lang)
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

                ## Respond via Ajax
                if request.is_ajax:
                    return JsonResponse({
                                'last_saved' : trans_node.timestamp,
                                'success'    : True,
                            })

            last_saved = trans_node.timestamp

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
    context['last_saved']       = last_saved
    if context['orig_lang']: context['orig_font'] = fonts.noto[context['orig_lang'].font]
    if context['trans_lang']: context['trans_font'] = fonts.noto[context['trans_lang'].font]
    return render(request, 'ipho_exam/editor.html', context)


@login_required
def compiled_question(request, question_id, lang_id, raw_tex=False):
    trans = qquery.latest_version(question_id, lang_id)
    filename = u'IPhO16 - {} Q{} - {}.pdf'.format(trans.question.exam.name, trans.question.position, trans.lang.name)

    if trans.lang.is_pdf:
        # etag = md5(trans.node.pdf).hexdigest()
        # if request.META.get('HTTP_IF_NONE_MATCH', '') == etag:
        #     return HttpResponseNotModified()
        res = HttpResponse(trans.node.pdf, content_type="application/pdf")
        res['content-disposition'] = 'inline; filename="{}"'.format(filename.encode('utf-8'))
        # res['ETag'] = etag
        return res

    trans_content, ext_resources = trans.qml.make_tex()
    for r in ext_resources:
        if isinstance(r, tex.FigureExport):
            r.lang = trans.lang
    ext_resources.append(tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls'))
    context = {
                'polyglossia' : trans.lang.polyglossia,
                'font'        : fonts.noto[trans.lang.font],
                'extraheader' : trans.lang.extraheader,
                'lang_name'   : u'{} ({})'.format(trans.lang.name, trans.lang.delegation.country),
                'title'       : u'{} - {}'.format(trans.question.exam.name, trans.question.name),
                'is_answer'   : trans.question.is_answer_sheet(),
                'document'    : trans_content,
              }
    body = render_to_string('ipho_exam/tex/exam_question.tex', RequestContext(request,context)).encode("utf-8")

    if raw_tex:
        return HttpResponse(body, content_type="text/plain; charset=utf-8", charset="utf-8")
    try:
        return cached_responses.compile_tex(request, body, ext_resources, filename)
    except pdf.TexCompileException as e:
        return HttpResponse(e.log, content_type="text/plain")

@login_required
def pdf_exam_for_student(request, exam_id, student_id):
    exam = get_object_or_404(Exam, id=exam_id)
    student = get_object_or_404(Student, id=student_id)

    ## TODO: implement caching
    all_tasks = []

    student_languages = StudentSubmission.objects.filter(exam=exam, student=student)
    questions = exam.question_set.all()
    grouped_questions = {k: list(g) for k,g in itertools.groupby(questions, key=lambda q: q.position) }
    grouped_questions = OrderedDict(sorted(grouped_questions.iteritems()))
    for position, qgroup in grouped_questions.iteritems():
        question_task = question_utils.compile_stud_exam_question(qgroup, student_languages)
        result = question_task.delay()
        all_tasks.append(result)
        print 'Group', position, 'done.'
    filename = u'IPhO16 - {} - {}.pdf'.format(exam.name, student.code)
    chord_task = tasks.wait_and_concatenate.delay(all_tasks, filename)
    #chord_task = celery.chord(all_tasks, tasks.concatenate_documents.s(filename)).apply_async()
    return HttpResponseRedirect(reverse('exam:pdf-task', args=[chord_task.id]))

@login_required
def pdf_exam_pos_student(request, exam_id, position, student_id):
    exam = get_object_or_404(Exam, id=exam_id)
    student = get_object_or_404(Student, id=student_id)

    doc = get_object_or_404(Document, exam=exam_id, position=position, student=student_id)
    if hasattr(doc, 'documenttask'):
        task = AsyncResult(doc.documenttask.task_id)
        return render(request, 'ipho_exam/pdf_task.html', {'task': task})
    if doc.file:
        response = HttpResponse(doc.file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s' % doc.file.name
        return response

@login_required
def pdf_exam_pos_student_status(request, exam_id, position, student_id):
    exam = get_object_or_404(Exam, id=exam_id)
    student = get_object_or_404(Student, id=student_id)

    doc = get_object_or_404(Document, exam=exam_id, position=position, student=student_id)
    if not hasattr(doc, 'documenttask'):
        return JsonResponse({'status': 'COMPLETED', 'ready': True, 'failed': False})
    else:
        task = AsyncResult(doc.documenttask.task_id)
        return JsonResponse({'status': task.status, 'ready': task.ready(), 'failed': task.failed()})


@login_required
def task_status(request, token):
    task = AsyncResult(token)
    return JsonResponse({'status': task.status, 'ready': task.ready()})

@login_required
def pdf_task(request, token):
    task = AsyncResult(token)
    try:
        if task.ready():
            doc_pdf, meta = task.get()
            if request.META.get('HTTP_IF_NONE_MATCH', '') == meta['etag']:
                return HttpResponseNotModified()

            res = HttpResponse(doc_pdf, content_type="application/pdf")
            res['content-disposition'] = 'inline; filename="{}"'.format(meta['filename'].encode('utf-8'))
            res['ETag'] = meta['etag']
            return res
        else:
            return render(request, 'ipho_exam/pdf_task.html', {'task': task})
    except ipho_exam.pdf.TexCompileException as e:
        if request.user.is_superuser:
            return HttpResponse(e.log, content_type="text/plain")
        else:
            return render(request, 'ipho_exam/tex_error.html', {'error_code': e.code, 'task_id': task.id}, status=500)
