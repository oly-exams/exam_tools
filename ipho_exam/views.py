# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
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

from __future__ import print_function

from builtins import range
from builtins import object
from builtins import str, chr

import logging

# coding=utf-8
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotModified, JsonResponse, Http404, HttpResponseForbidden
from django.http.request import QueryDict

from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string
from django.db.models import Q, Count, Sum, Case, When, IntegerField, F, Max

import os
from copy import deepcopy
from collections import OrderedDict
from django.utils import timezone
from tempfile import mkdtemp
from hashlib import md5
import itertools

from django.conf import settings
from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, PDFNode, Language, Figure, CompiledFigure, RawFigure, Feedback, Like, StudentSubmission, ExamAction, TranslationImportTmp, Document, DocumentTask, PrintLog, Place
from ipho_exam import qml, tex, pdf, iphocode, qquery, fonts, cached_responses, question_utils
from ipho_exam.response import render_odt_response
from ipho_print import printer

from ipho_exam.forms import LanguageForm, FigureForm, TranslationForm, ExamQuestionForm, DeleteForm, VersionNodeForm, PDFNodeForm, FeedbackForm, AdminBlockForm, AdminBlockAttributeFormSet, AdminBlockAttributeHelper, SubmissionAssignForm, AssignTranslationForm, TranslationImportForm, AdminImportForm, PrintDocsForm, ScanForm, ExtraSheetForm

import ipho_exam
from ipho_exam import tasks
import celery
from celery.result import AsyncResult

logger = logging.getLogger('ipho_exam')
OFFICIAL_LANGUAGE = 1
OFFICIAL_DELEGATION = getattr(settings, 'OFFICIAL_DELEGATION')


def any_permission_required(*args):
    """
    A decorator which checks user has any of the given permissions.
    permission required can not be used in its place as that takes only a
    single permission.
    """

    def test_func(user):
        for perm in args:
            if user.has_perm(perm):
                return True
        return False

    return user_passes_test(test_func)


@login_required
def index(request):
    return render(request, 'ipho_exam/index.html')


@login_required
@ensure_csrf_cookie
def main(request):
    success = None

    delegation = Delegation.objects.filter(members=request.user)

    own_lang = None
    other_lang = None
    if delegation.count() > 0:
        own_lang = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
        other_lang = Language.objects.filter(hidden=False).exclude(delegation=delegation).order_by('name')
    else:
        other_lang = Language.objects.filter(hidden=False).order_by('name')

    ## Exam section
    exam_list = Exam.objects.filter(hidden=False, active=True)  # TODO: allow admin to see all exams
    exams_open = ExamAction.objects.filter(
        delegation=delegation, exam=exam_list, exam__active=True, action=ExamAction.TRANSLATION, status=ExamAction.OPEN
    ).values('exam__pk', 'exam__name')
    exams_closed = ExamAction.objects.filter(
        delegation=delegation, exam=exam_list, action=ExamAction.TRANSLATION, status=ExamAction.SUBMITTED
    ).values('exam__pk', 'exam__name')
    return render(
        request, 'ipho_exam/main.html', {
            'own_lang': own_lang,
            'other_lang': other_lang,
            'exam_list': exam_list,
            'exams_open': exams_open,
            'exams_closed': exams_closed,
            'success': success,
        }
    )


def time_response(request):
    return HttpResponse(timezone.now().isoformat(), content_type="text/plain")


@permission_required('ipho_core.is_delegation')
def wizard(request):
    delegation = Delegation.objects.filter(members=request.user)

    own_languages = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
    ## Exam section
    exam_list = Exam.objects.filter(hidden=False, active=True)
    open_submissions = ExamAction.objects.filter(
        exam=exam_list, exam__active=True, delegation=delegation, action=ExamAction.TRANSLATION, status=ExamAction.OPEN
    )
    closed_submissions = ExamAction.objects.filter(
        exam=exam_list, delegation=delegation, action=ExamAction.TRANSLATION, status=ExamAction.SUBMITTED
    )
    # Translations
    translations = TranslationNode.objects.filter(language=own_languages, question__exam=exam_list)

    return render(
        request, 'ipho_exam/wizard.html', {
            'own_languages': own_languages,
            'exam_list': exam_list,
            'exams_open': open_submissions,
            'exams_closed': closed_submissions,
            'translations': translations,
        }
    )


@permission_required('ipho_core.is_delegation')
@ensure_csrf_cookie
def translations_list(request):
    delegation = Delegation.objects.filter(members=request.user)

    # if request.is_ajax and 'exam_id' in request.GET:
    if 'exam_id' in request.GET:
        exam = get_object_or_404(Exam, id=request.GET['exam_id'])
        in_progress = ExamAction.is_in_progress(ExamAction.TRANSLATION, exam=exam, delegation=delegation)
        trans_list = TranslationNode.objects.filter(
            question__exam=exam, language__delegation=delegation
        ).order_by('language', 'question')
        pdf_list = PDFNode.objects.filter(
            question__exam=exam, language__delegation=delegation
        ).order_by('language', 'question')
        node_list = list(trans_list) + list(pdf_list)
        official_translations_vnode = VersionNode.objects.filter(
            question__exam=exam, language__delegation__name=OFFICIAL_DELEGATION, status='C'
        ).order_by('question', '-version')
        official_translations_tnode = TranslationNode.objects.filter(
            question__exam=exam, language__delegation__name=OFFICIAL_DELEGATION
        ).order_by('question')
        official_nodes = []
        qdone = set()
        for node in official_translations_vnode:
            if node.question not in qdone:
                official_nodes.append(node)
                qdone.add(node.question)
        official_nodes += list(official_translations_tnode)
        return render(
            request, 'ipho_exam/partials/list_exam_tbody.html', {
                'exam': exam,
                'node_list': node_list,
                'official_nodes': official_nodes,
                'exam_active': exam.active and in_progress
            }
        )
    else:
        exam_list = Exam.objects.filter(hidden=False, active=True)
        for exam in exam_list:
            exam.is_active = exam.active and ExamAction.is_in_progress(
                ExamAction.TRANSLATION, exam=exam, delegation=delegation
            )
        return render(request, 'ipho_exam/list.html', {
            'exam_list': exam_list,
        })


@login_required
@ensure_csrf_cookie
def list_all_translations(request):
    exams = Exam.objects.filter(hidden=False, active=True)
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

    trans_list = TranslationNode.objects.filter(
        question__exam=filter_ex, language__delegation=filter_dg
    ).order_by('language__delegation', 'question')
    pdf_list = PDFNode.objects.filter(
        question__exam=filter_ex, language__delegation=filter_dg
    ).order_by('language__delegation', 'question')
    all_nodes = list(trans_list) + list(pdf_list)

    paginator = Paginator(all_nodes, 25)  # Show 25 contacts per page

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
            for k, v in list(self.get.items()):
                qdict[k] = v
            for k, v in list(kwargs.items()):
                if v is None:
                    if k in qdict: del qdict[k]
                else:
                    qdict[k] = v
            url = self.url + '?' + qdict.urlencode()
            return url

    return render(
        request, 'ipho_exam/list_all.html', {
            'exams': exams,
            'exam': exam,
            'delegations': delegations,
            'delegation': delegation,
            'node_list': node_list,
            'all_pages': list(range(1, paginator.num_pages + 1)),
            'this_url_builder': url_builder(reverse('exam:list-all'), request.GET),
        }
    )


@permission_required('ipho_core.is_delegation')
def add_translation(request, exam_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    delegation = Delegation.objects.get(members=request.user)
    exam = get_object_or_404(Exam, id=exam_id)
    ExamAction.require_in_progress(ExamAction.TRANSLATION, exam=exam, delegation=delegation)

    num_questions = exam.question_set.count()
    translation_form = TranslationForm(request.POST or None)
    translation_form.fields['language'].queryset = Language.objects.filter(delegation=delegation).annotate(
        num_translation=Sum(
            Case(
                When(Q(translationnode__question__exam=exam, is_pdf=False), then=1),
                When(is_pdf=True, then=None),
                output_field=IntegerField(),
                default=0
            )
        ),
        num_pdf=Sum(
            Case(
                When(Q(pdfnode__question__exam=exam, is_pdf=True), then=1),
                When(is_pdf=False, then=None),
                output_field=IntegerField(),
                default=0
            )
        )
    ).filter(Q(num_translation__lt=num_questions) | Q(num_pdf__lt=num_questions))
    if translation_form.is_valid():
        failed_questions = []
        for question in exam.question_set.exclude(translationnode__language=translation_form.cleaned_data['language']):
            if translation_form.cleaned_data['language'].is_pdf:
                node, _ = PDFNode.objects.get_or_create(
                    language=translation_form.cleaned_data['language'], question=question, defaults={'status': 'O'}
                )
            elif question.has_published_version():
                node, _ = TranslationNode.objects.get_or_create(
                    language=translation_form.cleaned_data['language'], question=question, defaults={'status': 'O'}
                )
                trans = deepcopy(qquery.latest_version(question_id=question.pk, lang_id=OFFICIAL_LANGUAGE))
                data = {key: u'\xa0' for key in list(trans.qml.get_data().keys())}
                trans.qml.update(data)
                node.text = qml.xml2string(trans.qml.make_xml())
                node.save()
            else:
                failed_questions.append(question.name)

        if failed_questions:
            # raise ValueError(failed_questions)
            return JsonResponse({
                'success':
                True,
                'added_all':
                False,
                'message':
                '<strong>Warning!</strong> Translation{1} could not be added for the following question{1}: {0}'.format(
                    ', '.join(failed_questions), 's' if len(failed_questions) > 1 else ''
                ),
                'exam_id':
                exam.pk,
            })
        else:
            return JsonResponse({
                'success':
                True,
                'added_all':
                True,
                'message':
                '<strong>Translation added!</strong> The new translation has successfully been added.',
                'exam_id':
                exam.pk,
            })

    form_html = render_crispy_form(translation_form)
    return JsonResponse({
        'title': 'Add translation to {}'.format(exam.name),
        'form': form_html,
        'submit_text': 'Add',
        'success': False,
    })


@permission_required('ipho_core.is_delegation')
def add_pdf_node(request, question_id, lang_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    delegation = Delegation.objects.get(members=request.user)
    question = get_object_or_404(Question, id=question_id)
    lang = get_object_or_404(Language, id=lang_id)
    if not lang.check_permission(request.user):
        return HttpResponseForbidden('You do not have the permissions to edit this language.')

    ExamAction.require_in_progress(ExamAction.TRANSLATION, exam=question.exam, delegation=delegation)

    node = get_object_or_404(PDFNode, question=question, language=lang)
    ## Language section
    node_form = PDFNodeForm(request.POST or None, request.FILES or None, instance=node)
    if node_form.is_valid():
        node_form.save()

        return JsonResponse({
            'success':
            True,
            'message':
            '<strong>PDF uploaded!</strong> The translation of {} in <emph>{}</emph> has been updated.'.format(
                question.name, lang.name
            ),
        })

    form_html = render_crispy_form(node_form)
    return JsonResponse({
        'title': 'Upload new version',
        'form': form_html,
        'submit': 'Upload',
        'success': False,
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
    res['content-disposition'] = 'attachment; filename="{}"'.format(
        'exam_export_q{}_l{}.xml'.format(question_id, lang_id)
    )
    return res


@permission_required('ipho_core.is_delegation')
def translation_import(request, question_id, lang_id):
    delegation = Delegation.objects.filter(members=request.user)
    language = get_object_or_404(Language, id=lang_id)
    question = get_object_or_404(Question, id=question_id)
    if not language.check_permission(request.user):
        return HttpResponseForbidden('You do not have the permissions to edit this language.')

    ExamAction.require_in_progress(ExamAction.TRANSLATION, exam=question.exam, delegation=delegation)

    form = TranslationImportForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        txt = request.FILES['file'].read()
        try:
            txt = txt.decode('utf8')
        except AttributeError:
            pass
        obj.content = qml.normalize_html(txt)
        obj.question = question
        obj.language = language
        obj.save()
        return HttpResponseRedirect(reverse('exam:import-translation-confirm', args=(str(obj.slug), )))

    form_html = render_crispy_form(form)
    return JsonResponse({
        'title': 'Import question',
        'form': form_html,
        'submit': 'Upload',
        'success': False,
    })


@permission_required('ipho_core.is_delegation')
@csrf_protect
def translation_import_confirm(request, slug):
    trans_import = get_object_or_404(TranslationImportTmp, slug=slug)
    trans = qquery.latest_version(trans_import.question.pk, trans_import.language.pk)

    if request.POST:
        trans.node.text = trans_import.content
        trans.node.save()
        trans_import.delete()

        return JsonResponse({
            'success':
            True,
            'message':
            '<strong>Question imported!</strong> The translation of {} in <emph>{}</emph> has been updated.'.format(
                trans.question.name, trans.lang.name
            ),
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
        'title': 'Review the changes before accepting the new version',
        'form': form_html,
        'submit': 'Confirm',
        'href': reverse('exam:import-translation-confirm', args=(slug, )),
        'success': False,
    })


@permission_required('ipho_core.is_delegation')
@ensure_csrf_cookie
def list_language(request):
    delegation = Delegation.objects.filter(members=request.user)
    languages = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
    # TODO: do not show Add language if no delegation
    return render(request, 'ipho_exam/languages.html', {'languages': languages})


@permission_required('ipho_core.is_delegation')
def add_language(request):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    delegation = Delegation.objects.get(members=request.user)

    ## Language section
    language_form = LanguageForm(request.POST or None, user_delegation=delegation)

    if language_form.is_valid():
        lang = language_form.instance.delegation = delegation
        lang = language_form.save()

        languages = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
        return JsonResponse({
            'type':
            'add',
            'name':
            lang.name,
            'href':
            reverse('exam:language-edit', args=[lang.pk]),
            'tbody':
            render_to_string('ipho_exam/partials/languages_tbody.html', {'languages': languages}),
            'success':
            True,
            'message':
            '<strong>Language created!</strong> The new languages has successfully been created.',
        })

    form_html = render_crispy_form(language_form)
    return JsonResponse({
        'title': 'Add new language',
        'form': form_html,
        'submit': 'Create',
        'success': False,
    })


@permission_required('ipho_core.is_delegation')
def edit_language(request, lang_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    delegation = Delegation.objects.get(members=request.user)

    instance = get_object_or_404(Language, pk=lang_id)
    language_form = LanguageForm(request.POST or None, instance=instance, user_delegation=delegation)
    if language_form.is_valid():
        lang = language_form.save()

        languages = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
        return JsonResponse({
            'type':
            'edit',
            'name':
            lang.name,
            'href':
            reverse('exam:language-edit', args=[lang.pk]),
            'tbody':
            render_to_string('ipho_exam/partials/languages_tbody.html', {'languages': languages}),
            'success':
            True,
            'message':
            '<strong>Language modified!</strong> The language ' + lang.name + ' has successfully been modified.',
        })

    form_html = render_crispy_form(language_form)
    return JsonResponse({
        'title': 'Edit language',
        'form': form_html,
        'submit': 'Save',
        'success': False,
    })


@login_required
@ensure_csrf_cookie
def feedbacks_list(request):
    exam_list = Exam.objects.filter(hidden=False, active=True)
    delegation = Delegation.objects.filter(members=request.user)

    if 'exam_id' in request.GET:
        if not int(request.GET['exam_id']) in [ex.pk for ex in exam_list]:
            raise Http404('Not such active exam.')
        questions = Question.objects.filter(exam=request.GET['exam_id'])
        feedbacks = Feedback.objects.filter(question=questions).annotate(
            num_likes=Sum(Case(When(like__status='L', then=1), output_field=IntegerField())),
            num_unlikes=Sum(Case(When(like__status='U', then=1), output_field=IntegerField())),
            delegation_likes=Sum(
                Case(When(like__delegation=delegation, then=1), default=0, output_field=IntegerField())
            )
        ).values(
            'num_likes', 'num_unlikes', 'delegation_likes', 'pk', 'question__pk', 'question__name',
            'question__feedback_active', 'delegation__name', 'delegation__country', 'status', 'timestamp', 'part',
            'comment'
        ).order_by('question__position')
        choices = dict(Feedback._meta.get_field_by_name('status')[0].flatchoices)
        for fb in feedbacks:
            fb['status_display'] = choices[fb['status']]
            fb['enable_likes'
               ] = (fb['delegation_likes'] == 0) and fb['question__feedback_active'] and len(delegation) > 0
        feedbacks = list(feedbacks)
        feedbacks.sort(key=lambda fb: (fb['question__pk'], Feedback.part_id(fb['part'])))
        return render(
            request, 'ipho_exam/partials/feedbacks_tbody.html', {
                'feedbacks': feedbacks,
                'status_choices': Feedback.STATUS_CHOICES,
                'is_delegation': len(delegation) > 0 or request.user.has_perm('ipho_core.is_staff'),
            }
        )
    else:
        # TODO: allow Add feedback only if a delegation
        return render(
            request, 'ipho_exam/feedbacks.html', {
                'exam_list': exam_list,
                'is_delegation': len(delegation) > 0 or request.user.has_perm('ipho_core.is_staff'),
            }
        )


@any_permission_required('ipho_core.is_delegation', 'ipho_core.is_staff')
def feedbacks_add(request, exam_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    if request.user.has_perm('ipho_core.is_staff'):
        delegation = Delegation.objects.get(name=OFFICIAL_DELEGATION)
    else:
        delegation = Delegation.objects.get(members=request.user)

    ## Language section
    form = FeedbackForm(request.POST or None)
    form.fields['question'].queryset = Question.objects.filter(exam=exam_id, exam__hidden=False, feedback_active=True)
    if form.is_valid():
        form.instance.delegation = delegation
        form.instance.part = '{}.{}'.format(form.cleaned_data['part_nr'], form.cleaned_data['subpart_nr'])
        form.save()

        return JsonResponse({
            'success':
            True,
            'message':
            '<strong>Feedback added!</strong> The new feedback has successfully been added. The staff will look at it.',
            'exam_id':
            exam_id,
        })

    form_html = render_crispy_form(form)
    return JsonResponse({
        'title': 'Add new feedback',
        'form': form_html,
        'submit': 'Submit',
        'success': False,
    })


@permission_required('ipho_core.is_delegation')
def feedback_like(request, status, feedback_id):
    feedback = get_object_or_404(Feedback, pk=feedback_id, question__feedback_active=True)
    delegation = Delegation.objects.get(members=request.user)
    Like.objects.get_or_create(feedback=feedback, delegation=delegation, defaults={'status': status})
    return redirect('exam:feedbacks-list')


@permission_required('ipho_core.is_staff')
def feedback_set_status(request, feedback_id, status):
    fb = get_object_or_404(Feedback, id=feedback_id)
    fb.status = status
    fb.save()
    return redirect('exam:feedbacks-list')


@permission_required('ipho_core.is_staff')
def feedbacks_export(request):
    questions = Question.objects.all().order_by('exam', 'position', 'type')
    return render(request, 'ipho_exam/admin_feedbacks_export.html', {
        'questions': questions,
    })


@permission_required('ipho_core.is_staff')
def feedbacks_export_csv(request, exam_id, question_id):
    feedbacks = Feedback.objects.filter(
        question=question_id,
    ).annotate(
        num_likes=Sum(Case(When(like__status='L', then=1), output_field=IntegerField())),
        num_unlikes=Sum(Case(When(like__status='U', then=1), output_field=IntegerField()))
    ).values_list(
        'pk', 'question__exam__name', 'question__name', 'part', 'delegation__name', 'status', 'timestamp', 'comment',
        'num_likes', 'num_unlikes'
    ).order_by('-timestamp')

    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Feedbacks_E{}_{}.csv"'.format(exam_id, question_id)

    writer = csv.writer(response)
    writer.writerow([
        'Id', 'Exam', 'Question', 'Part', 'Delegation', 'Status', 'Timestamp', 'Comment', 'Num likes', 'Num unlikes'
    ])

    for row in feedbacks:
        writer.writerow(row)

    return response


@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def figure_list(request):
    figure_list = Figure.objects.all()

    return render(request, 'ipho_exam/figures.html', {
        'figure_list': figure_list,
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
        ext = os.path.splitext(str(request.FILES['file']))[1]

        if ext in ['.svg', '.svgz']:
            obj = CompiledFigure.objects.create(name=obj.name)
            obj.content = request.FILES['file'].read()
            placeholders = figparam_placeholder.findall(obj.content)
            obj.params = ','.join(placeholders)
            obj.save()
        else:
            obj = RawFigure.objects.create(name=obj.name)
            obj.content = request.FILES['file'].read()
            obj.filetype = ext.lstrip('.')
            obj.save()

        return JsonResponse({
            'type': 'add',
            'figid': obj.pk,
            'name': obj.name,
            'params': obj.params,
            'src': reverse('exam:figure-export', args=[obj.pk]),
            'edit-href': reverse('exam:figure-edit', args=[obj.pk]),
            'delete-href': reverse('exam:figure-delete', args=[obj.pk]),
            'success': True,
            'message': '<strong>Figure added!</strong> The new figure has successfully been created.',
        })

    form_html = render_crispy_form(form)
    return JsonResponse({
        'title': 'Add new figure',
        'form': form_html,
        'submit': 'Upload',
        'success': False,
    })


@permission_required('ipho_core.is_staff')
def figure_edit(request, fig_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')

    instance = get_object_or_404(Figure, pk=fig_id)
    if isinstance(instance, RawFigure):
        compiled = False
        valid_extensions = ('.' + instance.filetype, )
    elif isinstance(instance, CompiledFigure):
        compiled = True
        valid_extensions = ('.svg', '.svgz')
    # The 'else' case should produce an error, since Figures should never be neither Raw nor Compiled.
    form = FigureForm(request.POST or None, request.FILES or None, instance=instance, valid_extensions=valid_extensions)
    if form.is_valid():
        obj = form.save(commit=False)
        if 'file' in request.FILES:
            if compiled:
                obj.content = request.FILES['file'].read()
                placeholders = figparam_placeholder.findall(obj.content)
                obj.params = ','.join(placeholders)
                obj.save()
            else:
                obj.content = request.FILES['file'].read()
                obj.save()

        return JsonResponse({
            'type':
            'edit',
            'figid':
            obj.pk,
            'name':
            obj.name,
            'params':
            obj.params,
            'src':
            reverse('exam:figure-export', args=[obj.pk]),
            'edit-href':
            reverse('exam:figure-edit', args=[obj.pk]),
            'delete-href':
            reverse('exam:figure-delete', args=[obj.pk]),
            'success':
            True,
            'message':
            '<strong>Figure modified!</strong> The figure ' + obj.name + ' has successfully been modified.',
        })

    form_html = render_crispy_form(form)
    return JsonResponse({
        'title': 'Edit figure',
        'form': form_html,
        'submit': 'Save',
        'success': False,
    })


@permission_required('ipho_core.is_staff')
def figure_delete(request, fig_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    obj = get_object_or_404(Figure, pk=fig_id)
    obj.delete()
    return JsonResponse({
        'success': True,
    })


@login_required
def figure_export(request, fig_id, lang_id=None):
    lang = get_object_or_404(Language, pk=lang_id) if lang_id is not None else None
    fig = get_object_or_404(Figure, pk=fig_id)
    figure_content, content_type = fig.to_inline(query=request.GET, lang=lang)
    return HttpResponse(figure_content, content_type="image/{}".format(content_type))


@permission_required('ipho_core.is_staff')
def admin_add_question(request, exam_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')

    ## Question section
    question_form = ExamQuestionForm(request.POST or None)
    exam = get_object_or_404(Exam, id=exam_id)

    if question_form.is_valid():
        question_form.instance.exam = exam
        if question_form.cleaned_data.get('type') != Question.ANSWER:
            question_form.instance.working_pages = 0
        question_form.save()

        return JsonResponse({
            'type':
            'submit',
            'success':
            True,
            'message':
            '<strong>Question created!</strong> The new question ' + question_form.cleaned_data.get('name') +
            ' has successfully been created.',
            'exam_id':
            exam_id,
        })

    form_html = render_crispy_form(question_form)
    return JsonResponse({
        'title': 'Add new question',
        'form': form_html,
        'submit': 'Create',
        'success': False,
    })


@permission_required('ipho_core.is_staff')
def admin_delete_question(request, exam_id, question_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')

    delete_form = DeleteForm(request.POST or None)

    delete_message = 'This action <strong>CANNOT</strong> be undone. <strong>All versions and all translations</strong> of this question will be lost.'

    if delete_form.is_valid():
        question = get_object_or_404(Question, id=question_id)
        if question.name == delete_form.cleaned_data.get('verify'):
            question.delete()
            return JsonResponse({
                'type':
                'submit',
                'success':
                True,
                'message':
                '<strong>Question deleted!</strong> The question ' + question.name + ' has been deleted.',
                'exam_id':
                exam_id,
            })
        else:
            form_html = render_crispy_form(delete_form)
            return JsonResponse({
                        'title'   : 'Are you sure?',
                        'form'    : '<div class="alert alert-warning alert-dismissible"><button type="button" class="close" data-dismiss="alert"><span>&times;</span></button>'\
                                    +'<strong>Try again!</strong> The question name does not match.</div>'\
                                    +delete_message\
                                    +form_html,
                        'success' : False,
                    })

    form_html = render_crispy_form(delete_form)
    return JsonResponse({
                'title'   : 'Are you sure?',
                'form'    : delete_message\
                            +form_html,
                'success' : False,
            })


@permission_required('ipho_core.is_staff')
def admin_edit_question(request, exam_id, question_id):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')

    ## Question section
    instance = get_object_or_404(Question, pk=question_id)
    question_form = ExamQuestionForm(request.POST or None, instance=instance)

    if question_form.is_valid():
        if question_form.cleaned_data.get('type') != Question.ANSWER:
            question_form.instance.working_pages = 0
        question = question_form.save()

        return JsonResponse({
            'type':
            'submit',
            'success':
            True,
            'message':
            '<strong>Question modified!</strong> The question ' + question.name + ' has successfully been modified.',
            'exam_id':
            exam_id,
        })

    form_html = render_crispy_form(question_form)
    return JsonResponse({
        'title': 'Edit question',
        'form': form_html,
        'submit': 'Save',
        'success': False,
    })


@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def admin_list(request):
    if request.is_ajax and 'exam_id' in request.GET:
        exam = get_object_or_404(Exam, id=request.GET['exam_id'])
        return JsonResponse({
            'content': render_to_string('ipho_exam/partials/admin_exam_tbody.html', {'exam': exam}),
        })
    else:
        exam_list = Exam.objects.filter(hidden=False)
        return render(request, 'ipho_exam/admin.html', {
            'exam_list': exam_list,
        })


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
            node = VersionNode(question=question, language=lang, version=0, text='<question id="q0" />')
    else:
        node = get_object_or_404(TranslationNode, question=question, language=lang)

    if lang.versioned:  ## make new version and increase version number
        node.pk = None
        node.tag = None
        node.version += 1
        node.status = 'P'
    node.save()

    return JsonResponse({'success': True})


@permission_required('ipho_core.is_staff')
def admin_import_version(request, question_id):
    language = get_object_or_404(Language, id=OFFICIAL_LANGUAGE)
    question = get_object_or_404(Question, id=question_id)

    form = AdminImportForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        txt = request.FILES['file'].read()
        try:
            txt = txt.decode('utf8')
        except AttributeError:
            pass
        if language.versioned:
            if VersionNode.objects.filter(question=question, language=language).exists():
                node = VersionNode.objects.filter(question=question, language=language).order_by('-version')[0]
            else:
                node = VersionNode(question=question, language=language, version=0, text='<question id="q0" />')
        else:
            node = get_object_or_404(TranslationNode, question=question, language=language)

        if language.versioned:  ## make new version and increase version number
            node.pk = None
            node.version += 1
            node.status = 'P'
        node.text = qml.escape_equations(txt)
        node.save()
        return JsonResponse({'success': True})

    form_html = render_crispy_form(form)
    return JsonResponse({
        'title': 'Import question',
        'form': form_html,
        'submit': 'Upload',
        'success': False,
    })


@permission_required('ipho_core.is_staff')
def admin_delete_version(request, exam_id, question_id, version_num):
    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)
    lang = get_object_or_404(Language, id=lang_id)

    if lang.versioned:
        node = get_object_or_404(VersionNode, question=question, language=lang, status='P', version=version_num)
    else:
        raise Exception('Only versioned node can be deleted')

    delete_form = DeleteForm(request.POST or None)

    delete_message = 'This action <strong>CANNOT</strong> be undone. All changes made in this version will be lost.'

    if delete_form.is_valid():
        if question.name == delete_form.cleaned_data.get('verify'):
            node.delete()
            return JsonResponse({
                'type':
                'submit',
                'success':
                True,
                'message':
                '<strong>Version deleted!</strong> Version v' + str(node.version) + ' of question ' + question.name +
                ' has been deleted.',
                'exam_id':
                exam_id,
            })
        else:
            form_html = render_crispy_form(delete_form)
            return JsonResponse({
                        'title'   : 'Are you sure?',
                        'form'    : '<div class="alert alert-warning alert-dismissible"><button type="button" class="close" data-dismiss="alert"><span>&times;</span></button>'\
                                    +'<strong>Try again!</strong> The question name does not match.</div>'\
                                    +delete_message\
                                    +form_html,
                        'success' : False,
                    })

    form_html = render_crispy_form(delete_form)
    return JsonResponse({
                'title'   : 'Are you sure?',
                'form'    : delete_message\
                            +form_html,
                'success' : False,
            })


@permission_required('ipho_core.is_staff')
def admin_accept_version(request, exam_id, question_id, version_num, compare_version=None):
    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)

    lang = get_object_or_404(Language, id=lang_id)

    if not VersionNode.objects.filter(question=question, language=lang, status__in=['S', 'C']):
        node = get_object_or_404(VersionNode, question=question, language=lang, status='P', version=version_num)
        node.status = 'S'
        node.save()
        return HttpResponseRedirect(reverse('exam:admin'))

    if compare_version is None:
        compare_node = VersionNode.objects.filter(
            question=question, language=lang, status__in=['S', 'C']
        ).order_by('-version')[0]
        return HttpResponseRedirect(
            reverse(
                'exam:admin-accept-version-diff',
                kwargs=dict(
                    exam_id=exam.pk,
                    question_id=question.pk,
                    version_num=int(version_num),
                    compare_version=compare_node.version
                )
            )
        )

    if lang.versioned:
        node = get_object_or_404(VersionNode, question=question, language=lang, status='P', version=version_num)
        compare_node = get_object_or_404(
            VersionNode, question=question, language=lang, status__in=['S', 'C'], version=compare_version
        )
    else:
        ## TODO: add status check
        node = get_object_or_404(TranslationNode, question=question, language=lang)
        compare_node = get_object_or_404(TranslationNode, question=question, language=lang)

    ## Save and redirect
    if request.POST:
        node.status = 'S'
        node.save()
        return HttpResponseRedirect(reverse('exam:admin'))

    node_versions = []
    if lang.versioned:
        node_versions = VersionNode.objects.filter(
            question=question, language=lang, status__in=['S', 'C']
        ).order_by('-version').values_list(
            'version', flat=True
        )

    old_q = qml.make_qml(compare_node)
    old_data = old_q.get_data()
    new_q = qml.make_qml(node)
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


@permission_required('ipho_core.is_staff')
def admin_publish_version(request, exam_id, question_id, version_num):
    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)
    lang = get_object_or_404(Language, id=lang_id)

    if lang.versioned:
        node = get_object_or_404(VersionNode, question=question, language=lang, status='S', version=version_num)
    else:
        node = get_object_or_404(TranslationNode, question=question, language=lang)

    node.status = 'C'
    node.save()
    return HttpResponseRedirect(reverse('exam:admin'))


@permission_required('ipho_core.is_staff')
def admin_settag_version(request, exam_id, question_id, version_num):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')

    lang_id = OFFICIAL_LANGUAGE

    exam = get_object_or_404(Exam, id=exam_id)
    question = get_object_or_404(Question, id=question_id)
    lang = get_object_or_404(Language, id=lang_id)

    ## Version section
    node = get_object_or_404(VersionNode, question=question, language=lang, version=version_num)
    node_form = VersionNodeForm(request.POST or None, instance=node)

    if node_form.is_valid():
        node_form.save()
        return JsonResponse({
            'type': 'submit',
            'success': True,
            'message': '<strong>Tag set!</strong> The tag has successfully been modified.',
            'exam_id': exam_id,
        })

    form_html = render_crispy_form(node_form)
    return JsonResponse({
        'title': 'Set version tag',
        'form': form_html,
        'submit': 'Save',
        'success': False,
    })


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

    q = qml.make_qml(node)
    #content_set = qml.make_content(q)

    qml_types = [(qobj.tag, qobj.display_name) for qobj in qml.QMLobject.all_objects()]
    context = {
        'exam': exam,
        'question': question,
        'content_set': [q],
        'node_version': node_version,
        'qml_types': qml_types,
        'lang_id': lang_id,
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

    q = qml.make_qml(node)

    block = q.find(block_id)
    if block is None:
        raise Http404('block_id not found')

    heading = 'Edit ' + block.heading() if block.heading() is not None else 'Edit block'

    form = AdminBlockForm(block, request.POST or None)
    attrs_form = AdminBlockAttributeFormSet(
        request.POST or None, initial=[{
            'key': k,
            'value': v
        } for k, v in list(block.attributes.items())]
    )
    if form.is_valid() and attrs_form.is_valid():
        if 'block_content' in form.cleaned_data:
            block.data = form.cleaned_data['block_content']
            block.data_html = form.cleaned_data['block_content']
        block.attributes = dict([(ff.cleaned_data['key'], ff.cleaned_data['value']) for ff in attrs_form
                                 if ff.cleaned_data])
        node.text = qml.xml2string(q.make_xml())
        node.save()

        return JsonResponse({
            'title':
            heading,
            'content':
            block.content_html(),
            'attributes':
            render_to_string('ipho_exam/partials/admin_editor_attributes.html', {'attributes': block.attributes}),
            'success':
            True,
        })

    form_html = render_crispy_form(form)
    attrs_form_html = render_crispy_form(attrs_form, AdminBlockAttributeHelper())
    return JsonResponse({
        'title': heading,
        'form': form_html + attrs_form_html,
        'success': False,
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

    q = qml.make_qml(node)

    block = q.delete(block_id)
    node.text = qml.xml2string(q.make_xml())
    node.save()

    return JsonResponse({
        'success': True,
    })


@permission_required('ipho_core.is_staff')
def admin_editor_add_block(request, exam_id, question_id, version_num, block_id, tag_name, after_id=None):
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

    q = qml.make_qml(node)

    block = q.find(block_id)
    if block is None:
        raise Http404('block_id not found')

    newblock = block.add_child(qml.ET.fromstring(u'<{} />'.format(tag_name)), after_id=after_id)
    node.text = qml.xml2string(q.make_xml())
    node.save()

    qml_types = [(qobj.tag, qobj.display_name) for qobj in qml.QMLobject.all_objects()]
    ctx = {
        'fields_set': [newblock],
        'parent': block,
        'exam': exam,
        'node_version': node_version,
        'question': question,
        'qml_types': qml_types,
    }
    return JsonResponse({
        'new_block': render_to_string('ipho_exam/admin_editor_field.html', ctx),
        'success': True,
    })


@permission_required('ipho_core.is_staff')
def admin_editor_move_block(request, exam_id, question_id, version_num, parent_id, block_id, direction):
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

    q = qml.make_qml(node)

    parent_block = q.find(parent_id)
    if parent_block is None:
        raise Http404('parent_id not found')

    ix = parent_block.child_index(block_id)
    if ix is None:
        raise Http404('block_id not found in parent {}'.format(parent_id))

    if direction == 'up' and ix > 0:
        parent_block.children[ix], parent_block.children[ix - 1] = parent_block.children[ix
                                                                                         - 1], parent_block.children[ix]
    elif direction == 'down' and ix < len(parent_block.children) - 1:
        parent_block.children[ix + 1], parent_block.children[ix] = parent_block.children[ix], parent_block.children[ix
                                                                                                                    + 1]
    else:
        return JsonResponse({'success': False})

    node.text = qml.xml2string(q.make_xml())
    node.save()

    return JsonResponse({'success': True, 'direction': direction})


@permission_required('ipho_core.is_delegation')
def submission_exam_list(request):
    delegation = Delegation.objects.filter(members=request.user)

    exams_open = Exam.objects.filter(
        hidden=False, active=True
    ).exclude(
        delegation_status__in=ExamAction.objects.
        filter(delegation=delegation, action=ExamAction.TRANSLATION, status=ExamAction.SUBMITTED)
    ).distinct()
    exams_closed = Exam.objects.filter(
        hidden=False,
    ).filter(
        delegation_status__delegation=delegation,
        delegation_status__action=ExamAction.TRANSLATION,
        delegation_status__status=ExamAction.SUBMITTED
    ).distinct()
    return render(request, 'ipho_exam/submission_list.html', {'exams_open': exams_open, 'exams_closed': exams_closed})


def _get_submission_languages(exam, delegation):
    """Returns the languages which are valid for submission."""
    num_questions = exam.question_set.count()
    return Language.objects.all().annotate(
        num_translation=Sum(
            Case(
                When(Q(translationnode__question__exam=exam, is_pdf=False), then=1),
                When(is_pdf=True, then=None),
                output_field=IntegerField(),
                default=0
            )
        ),
        num_pdf=Sum(
            Case(
                When(Q(pdfnode__question__exam=exam, is_pdf=True), then=1),
                When(is_pdf=False, then=None),
                output_field=IntegerField(),
                default=0
            )
        )
    ).filter(
        Q(delegation__name=OFFICIAL_DELEGATION) & Q(hidden_from_submission=False)
        | (Q(delegation=delegation) & (Q(num_translation=num_questions) | Q(num_pdf=num_questions)))
    )


@permission_required('ipho_core.is_staff')
def admin_submissions_translation(request):
    remaining_countries = ExamAction.objects.filter(
        exam__active=True, action=ExamAction.TRANSLATION, status=ExamAction.OPEN
    ).exclude(delegation=Delegation.objects.get(name=OFFICIAL_DELEGATION)).values_list('delegation__country')

    remaining_countries = [country[0] + ',' for country in remaining_countries]
    if remaining_countries:
        remaining_countries[-1] = remaining_countries[-1][:-1]

    open_exams = len(remaining_countries)

    submitted_countries = ExamAction.objects.filter(
        exam__active=True, action=ExamAction.TRANSLATION, status=ExamAction.SUBMITTED
    ).exclude(delegation=Delegation.objects.get(name=OFFICIAL_DELEGATION)
              ).order_by('timestamp').values_list('delegation__country')

    submitted_countries = [country[0] + ',' for country in submitted_countries]
    if submitted_countries:
        submitted_countries[-1] = submitted_countries[-1][:-1]

    submitted_exams = len(submitted_countries)

    return render(
        request, 'ipho_exam/admin_submissions_translation.html', {
            'open_exams': open_exams,
            'submitted_exams': submitted_exams,
            'remaining_countries': remaining_countries,
            'submitted_countries': submitted_countries,
        }
    )


@permission_required('ipho_core.is_delegation')
def submission_exam_assign(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    delegation = Delegation.objects.get(members=request.user)
    num_questions = exam.question_set.count()
    languages = _get_submission_languages(exam, delegation)
    ex_submission, _ = ExamAction.objects.get_or_create(exam=exam, delegation=delegation, action=ExamAction.TRANSLATION)
    if ex_submission.status == ExamAction.SUBMITTED and not settings.DEMO_MODE:
        return HttpResponseRedirect(reverse('exam:submission-exam-submitted', args=(exam.pk, )))

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
        form = AssignTranslationForm(
            request.POST or None,
            prefix='stud-{}'.format(stud.pk),
            languages_queryset=languages,
            initial=dict(languages=stud_langs, main_language=stud_main_lang)
        )
        all_valid = all_valid and form.is_valid()
        with_errors = with_errors or form.errors
        submission_forms.append((stud, form))

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
            student_seat = Place.objects.get(exam=exam, student=student)
            questions = exam.question_set.all()
            grouped_questions = {k: list(g) for k, g in itertools.groupby(questions, key=lambda q: q.position)}
            for position, qgroup in list(grouped_questions.items()):
                doc, _ = Document.objects.get_or_create(exam=exam, student=student, position=position)
                cover_ctx = {'student': student, 'exam': exam, 'question': qgroup[0], 'place': student_seat.name}
                question_task = tasks.student_exam_document.s(qgroup, student_languages, cover=cover_ctx, commit=True)
                # question_task = question_utils.compile_stud_exam_question(qgroup, student_languages, cover=cover_ctx, commit=True)
                question_task.freeze()
                doc_task, _ = DocumentTask.objects.update_or_create(
                    document=doc, defaults={'task_id': question_task.id}
                )
                question_task.delay()

        ## Return
        return HttpResponseRedirect(reverse('exam:submission-exam-confirm', args=(exam.pk, )))

    empty_languages = Language.objects.filter(delegation=delegation).annotate(
        num_translation=Sum(
            Case(
                When(Q(translationnode__question__exam=exam, is_pdf=False), then=1),
                When(is_pdf=True, then=None),
                output_field=IntegerField(),
                default=0
            )
        ),
        num_pdf=Sum(
            Case(
                When(Q(pdfnode__question__exam=exam, is_pdf=True), then=1),
                When(is_pdf=False, then=None),
                output_field=IntegerField(),
                default=0
            )
        )
    ).filter(Q(num_translation__lt=num_questions) | Q(num_pdf__lt=num_questions))

    return render(
        request, 'ipho_exam/submission_assign.html', {
            'exam': exam,
            'delegation': delegation,
            'languages': languages,
            'empty_languages': empty_languages,
            'submission_forms': submission_forms,
            'with_errors': with_errors,
        }
    )


@permission_required('ipho_core.is_delegation')
def submission_exam_confirm(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    num_questions = exam.question_set.count()
    delegation = Delegation.objects.get(members=request.user)
    languages = _get_submission_languages(exam, delegation)
    form_error = ''

    ex_submission, _ = ExamAction.objects.get_or_create(exam=exam, delegation=delegation, action=ExamAction.TRANSLATION)
    if ex_submission.status == ExamAction.SUBMITTED and not settings.DEMO_MODE:
        return HttpResponseRedirect(reverse('exam:submission-exam-submitted', args=(exam.pk, )))

    documents = Document.objects.filter(exam=exam, student__delegation=delegation).order_by('student', 'position')
    all_finished = all([not hasattr(doc, 'documenttask') for doc in documents])

    if request.POST and all_finished:
        if 'agree-submit' in request.POST:
            ex_submission.status = ExamAction.SUBMITTED
            ex_submission.save()
            return HttpResponseRedirect(reverse('exam:submission-exam-submitted', args=(exam.pk, )))
        else:
            form_error = '<strong>Error:</strong> You have to agree on the final submission before continuing.'

    stud_documents = {k: list(g) for k, g in itertools.groupby(documents, key=lambda d: d.student.pk)}

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

    return render(
        request, 'ipho_exam/submission_confirm.html', {
            'exam': exam,
            'delegation': delegation,
            'languages': languages,
            'stud_documents': stud_documents,
            'all_finished': all_finished,
            'submission_status': ex_submission.status,
            'students_languages': assigned_student_language,
            'form_error': form_error,
        }
    )


@permission_required('ipho_core.is_delegation')
def submission_exam_submitted(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    delegation = Delegation.objects.get(members=request.user)
    languages = _get_submission_languages(exam, delegation)

    ex_submission, _ = ExamAction.objects.get_or_create(exam=exam, delegation=delegation, action=ExamAction.TRANSLATION)

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

    documents = Document.objects.filter(exam=exam, student__delegation=delegation).order_by('student', 'position')
    stud_documents = {k: list(g) for k, g in itertools.groupby(documents, key=lambda d: d.student.pk)}

    return render(
        request, 'ipho_exam/submission_submitted.html', {
            'exam': exam,
            'delegation': delegation,
            'languages': languages,
            'stud_documents': stud_documents,
            'submission_status': ex_submission.status,
            'students_languages': assigned_student_language,
        }
    )


@permission_required('ipho_core.is_staff')
def admin_submission_list(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    delegation = Delegation.objects.get(members=request.user)
    submissions = StudentSubmission.objects.filter(exam=exam, student__delegation=delegation)

    return render(request, 'ipho_exam/admin_submissions.html', {
        'exam': exam,
        'submissions': submissions,
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
        return HttpResponseRedirect(reverse('exam:admin-submission-list', args=(exam.pk, )))
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
    context = {
        'exam_id': exam_id,
        'question_id': question_id,
        'lang_id': question_id,
        'orig_id': orig_id,
        'orig_diff': orig_diff,
    }
    exam_list = Exam.objects.filter(hidden=False, active=True)  # TODO: allow admin to see all exams
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
    orig_diff_tag = None
    trans_lang = None
    last_saved = None
    checksum = None

    if exam_id is not None:
        exam = get_object_or_404(Exam, id=exam_id, active=True, hidden=False)
    if question_id is not None:
        question = get_object_or_404(Question, id=question_id, exam=exam)
    elif exam is not None and exam.question_set.count() > 0:
        question = exam.question_set.first()

    if not question.check_permission(request.user):
        return HttpResponseForbidden('You do not have the permissions to view this question.')

    delegation = Delegation.objects.filter(members=request.user)
    ExamAction.require_in_progress(ExamAction.TRANSLATION, exam=exam, delegation=delegation)

    ## TODO:
    ## * deal with errors when node not found: no content

    if question:
        orig_lang = get_object_or_404(Language, id=orig_id)

        if delegation.count() > 0:
            own_lang = Language.objects.filter(hidden=False, delegation=delegation).order_by('name')
        elif request.user.is_superuser:
            own_lang = Language.objects.all().order_by('name')

        official_question = qquery.latest_version(question_id=question.pk, lang_id=OFFICIAL_LANGUAGE)

        # try:
        ## TODO: make a free function
        if orig_lang.versioned:
            orig_node = VersionNode.objects.filter(
                question=question, language=orig_lang, status='C'
            ).order_by('-version')[0]
            orig_lang.version = orig_node.version
            orig_lang.tag = orig_node.tag
            question_versions = VersionNode.objects.values_list('version', 'tag').order_by('-version').filter(
                question=question, language=orig_lang, status='C'
            )[1:]
        else:
            orig_node = get_object_or_404(TranslationNode, question=question, language=orig_lang)

        question_langs = []
        ## officials
        official_list = []
        for vn in VersionNode.objects.filter(
            question=question, status='C', language__delegation__name=OFFICIAL_DELEGATION
        ).order_by('-version'):
            if not vn.language in official_list:
                official_list.append(vn.language)
                official_list[-1].version = vn.version
                official_list[-1].tag = vn.tag
        official_list += list(
            Language.objects.filter(translationnode__question=question, delegation__name=OFFICIAL_DELEGATION)
        )
        question_langs.append({'name': 'official', 'order': 0, 'list': official_list})
        ## own
        if delegation.count() > 0:
            question_langs.append({
                'name':
                'own',
                'order':
                1,
                'list':
                Language.objects.filter(translationnode__question=question, delegation=delegation)
            })
        ## others
        question_langs.append({
            'name':
            'others',
            'order':
            2,
            'list':
            Language.objects.filter(translationnode__question=question
                                    ).exclude(delegation=delegation).exclude(delegation__name=OFFICIAL_DELEGATION)
        })

        orig_q_raw = qml.make_qml(orig_node)
        orig_q = deepcopy(official_question.qml)
        orig_q_raw_data = orig_q_raw.get_data()
        orig_q_raw_data = {k: v for k, v in list(orig_q_raw_data.items()) if v}
        orig_q.update(orig_q_raw_data)
        orig_q.set_lang(orig_lang)

        if orig_diff is not None:
            if not orig_lang.versioned:
                raise Exception('Original language does not support versioning.')
            orig_diff_tag = orig_lang.tag
            orig_diff_node = get_object_or_404(VersionNode, question=question, language=orig_lang, version=orig_diff)
            orig_diff_q = qml.make_qml(orig_diff_node)
            orig_diff_data = orig_diff_q.get_data()

            ## make diff
            ## show diff, new elements
            ## don't show, removed elements (non-trivial insert in the tree)
            orig_q.diff_content_html(orig_diff_data)

        content_set = qml.make_content(orig_q)

        trans_content = {}
        if lang_id is not None:
            trans_lang = get_object_or_404(Language, id=lang_id)
            if not trans_lang.check_permission(request.user):
                return HttpResponseForbidden('You do not have the permissions to edit this language.')
            trans_node, created = TranslationNode.objects.get_or_create(
                question=question, language_id=lang_id, defaults={
                    'text': '',
                    'status': 'O'
                }
            )  ## TODO: check permissions for this.
            if len(trans_node.text) > 0:
                trans_q = qml.make_qml(trans_node)
                trans_q.set_lang(trans_lang)
                trans_content = trans_q.get_data()
                trans_extra_html = trans_q.get_trans_extra_html()
            checksum = md5(trans_node.text.encode('utf8')).hexdigest()
            form = qml.QMLForm(orig_q, trans_content, request.POST or None)

            if form.is_valid():
                q = deepcopy(orig_q)
                cleaned_data = form.cleaned_data
                for k in list(cleaned_data.keys()):
                    cleaned_data[k] = cleaned_data[k].replace(chr(8), u'').replace(chr(29), u'')
                q.update(cleaned_data, set_blanks=True)
                new_text = qml.xml2string(q.make_xml())
                new_checksum = md5(new_text.encode('utf8')).hexdigest()

                ## Nothing to do, the checksum is still the same
                if checksum == new_checksum:
                    return JsonResponse({
                        'last_saved': trans_node.timestamp.isoformat(),
                        'success': True,
                        'checksum': checksum,
                    })
                ## It is good to save
                elif request.POST.get('checksum', None) == checksum:
                    if trans_node.status == 'L':
                        raise Exception('The question cannot be modified. It is locked.')
                    if trans_node.status == 'S':
                        raise Exception('The question cannot be modified. It is already submitted.')
                    ## update the content in the original XML.
                    ## TODO: we could keep track of orig_v in the submission and, in case of updates, show a diff in the original language.
                    trans_node.text = new_text
                    trans_node.save()
                    checksum = new_checksum

                    ## Respond via Ajax: Saved and with new checksum
                    if request.is_ajax:
                        return JsonResponse({
                            'last_saved': trans_node.timestamp.isoformat(),
                            'checksum': checksum,
                            'success': True,
                        })
                ## Checksums mistach we have to abort and notify out-of-sync
                else:
                    logger.warning(
                        "Sync lost. incoming checksum '{}', existing checksum '{}'.\n\nThe POST request was:\n{}\n\n".
                        format(request.POST.get('checksum', None), checksum, request.POST)
                    )
                    return JsonResponse({
                        'success': False,
                        'checksum': checksum,
                    })

            last_saved = trans_node.timestamp

    # except:
    #     context['warning'] = 'This question does not have any content.'
    if context['orig_diff'] is not None:
        context['orig_diff'] = int(context['orig_diff'])
    context['exam'] = exam
    context['question'] = question
    context['question_langs'] = question_langs
    context['question_versions'] = question_versions
    context['own_lang'] = own_lang
    context['orig_lang'] = orig_lang
    context['orig_diff_tag'] = orig_diff_tag
    context['trans_lang'] = trans_lang
    context['content_set'] = content_set
    context['form'] = form
    context['trans_extra_html'] = trans_extra_html
    context['last_saved'] = last_saved
    context['checksum'] = checksum
    if context['orig_lang']:
        context['orig_font'] = fonts.ipho[context['orig_lang'].font]
    if context['trans_lang']:
        context['trans_font'] = fonts.ipho[context['trans_lang'].font]
    return render(request, 'ipho_exam/editor.html', context)


@login_required
def compiled_question(request, question_id, lang_id, version_num=None, raw_tex=False):
    if not Question.objects.get(pk=question_id).check_permission(request.user):
        return HttpResponseForbidden('You do not have the permissions to view this question.')
    if version_num is not None and request.user.has_perm('ipho_core.is_staff'):
        trans = qquery.get_version(question_id, lang_id, version_num)
    else:
        trans = qquery.latest_version(question_id, lang_id)

    filename = u'Exam - {} Q{} - {}.pdf'.format(trans.question.exam.name, trans.question.position, trans.lang.name)

    if trans.lang.is_pdf:
        # etag = md5(trans.node.pdf).hexdigest()
        # if request.META.get('HTTP_IF_NONE_MATCH', '') == etag:
        #     return HttpResponseNotModified()
        res = HttpResponse(trans.node.pdf, content_type="application/pdf")
        res['content-disposition'] = 'inline; filename="{}"'.format(filename)
        # res['ETag'] = etag
        return res

    trans_content, ext_resources = trans.qml.make_tex()
    for r in ext_resources:
        if isinstance(r, tex.FigureExport):
            r.lang = trans.lang
    ext_resources.append(tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls'))
    context = {
        'polyglossia': trans.lang.polyglossia,
        'polyglossia_options': trans.lang.polyglossia_options,
        'font': fonts.ipho[trans.lang.font],
        'extraheader': trans.lang.extraheader,
        'lang_name': u'{} ({})'.format(trans.lang.name, trans.lang.delegation.country),
        'exam_name': u'{}'.format(trans.question.exam.name),
        'code': u'{}{}'.format(trans.question.code, trans.question.position),
        'title': u'{} - {}'.format(trans.question.exam.name, trans.question.name),
        'is_answer': trans.question.is_answer_sheet(),
        'document': trans_content,
    }
    body = render_to_string('ipho_exam/tex/exam_question.tex', RequestContext(request, context))

    if raw_tex:
        return HttpResponse(body, content_type="text/plain; charset=utf-8", charset="utf-8")
    try:
        return cached_responses.compile_tex(request, body, ext_resources, filename)
    except pdf.TexCompileException as e:
        return HttpResponse(e.log, content_type="text/plain")


@login_required
def compiled_question_odt(request, question_id, lang_id, version_num=None):
    if not Question.objects.get(pk=question_id).check_permission(request.user):
        return HttpResponseForbidden('You do not have the permissions to view this question.')
    if version_num is not None and request.user.has_perm('ipho_core.is_staff'):
        trans = qquery.get_version(question_id, lang_id, version_num)
    else:
        trans = qquery.latest_version(question_id, lang_id)
    filename = u'Exam - {} Q{} - {}.odt'.format(trans.question.exam.name, trans.question.position, trans.lang.name)

    trans_content, ext_resources = trans.qml.make_xhtml()
    for r in ext_resources:
        if isinstance(r, tex.FigureExport):
            r.lang = trans.lang
    context = {
        'lang_name': u'{} ({})'.format(trans.lang.name, trans.lang.delegation.country),
        'title': u'{} - {}'.format(trans.question.exam.name, trans.question.name),
        'document': trans_content,
    }
    return render_odt_response(
        'ipho_exam/odt/exam_question.odt', RequestContext(request, context), filename, ext_resources
    )


@login_required
def compiled_question_html(request, question_id, lang_id, version_num=None):
    if not Question.objects.get(pk=question_id).check_permission(request.user):
        return HttpResponseForbidden('You do not have the permissions to view this question.')
    if version_num is not None and request.user.has_perm('ipho_core.is_staff'):
        trans = qquery.get_version(question_id, lang_id, version_num)
    else:
        trans = qquery.latest_version(question_id, lang_id)
    trans_content, ext_resources = trans.qml.make_xhtml()
    return HttpResponse(trans_content)


@login_required
def pdf_exam_for_student(request, exam_id, student_id):
    exam = get_object_or_404(Exam, id=exam_id)
    student = get_object_or_404(Student, id=student_id)

    ## TODO: implement caching
    all_tasks = []

    student_languages = StudentSubmission.objects.filter(exam=exam, student=student)
    questions = exam.question_set.all()
    grouped_questions = {k: list(g) for k, g in itertools.groupby(questions, key=lambda q: q.position)}
    grouped_questions = OrderedDict(sorted(grouped_questions.items()))
    for position, qgroup in list(grouped_questions.items()):
        question_task = question_utils.compile_stud_exam_question(qgroup, student_languages)
        result = question_task.delay()
        all_tasks.append(result)
        print('Group', position, 'done.')
    filename = u'Exam - {} - {}.pdf'.format(exam.name, student.code)
    chord_task = tasks.wait_and_concatenate.delay(all_tasks, filename)
    #chord_task = celery.chord(all_tasks, tasks.concatenate_documents.s(filename)).apply_async()
    return HttpResponseRedirect(reverse('exam:pdf-task', args=[chord_task.id]))


@login_required
def pdf_exam_pos_student(request, exam_id, position, student_id, type='P'):
    exam = get_object_or_404(Exam, id=exam_id)
    student = get_object_or_404(Student, id=student_id)

    doc = get_object_or_404(Document, exam=exam_id, position=position, student=student_id)
    if type == 'P':  ## for for printouts
        if hasattr(doc, 'documenttask'):
            task = AsyncResult(doc.documenttask.task_id)
            return render(request, 'ipho_exam/pdf_task.html', {'task': task})
        if doc.file:
            response = HttpResponse(doc.file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=%s' % doc.file.name
            return response
    elif type == 'S':  ## look for scans
        if doc.scan_file:
            response = HttpResponse(doc.scan_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=%s' % doc.scan_file.name
            return response
        else:
            raise Http404('Scan document not found')
    elif type == 'O':  ## look for scans
        if doc.scan_file_orig:
            response = HttpResponse(doc.scan_file_orig, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=%s' % doc.scan_file_orig.name.replace(' ', '_')
            return response
        else:
            raise Http404('Scan document not found')


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
def task_log(request, token):
    task = AsyncResult(token)
    try:
        if task.ready():
            doc_pdf, meta = task.get()
            return HttpResponse('NO LOG', content_type="text/plain")
        else:
            return render(request, 'ipho_exam/pdf_task.html', {'task': task})
    except ipho_exam.pdf.TexCompileException as e:
        return HttpResponse(e.log, content_type="text/plain")


@login_required
def pdf_task(request, token):
    task = AsyncResult(token)
    try:
        if task.ready():
            doc_pdf, meta = task.get()
            if request.META.get('HTTP_IF_NONE_MATCH', '') == meta['etag']:
                return HttpResponseNotModified()

            res = HttpResponse(doc_pdf, content_type="application/pdf")
            res['content-disposition'] = 'inline; filename="{}"'.format(meta['filename'])
            res['ETag'] = meta['etag']
            return res
        else:
            return render(request, 'ipho_exam/pdf_task.html', {'task': task})
    except ipho_exam.pdf.TexCompileException as e:
        if request.user.is_superuser:
            return HttpResponse(e.log, content_type="text/plain")
        else:
            return render(request, 'ipho_exam/tex_error.html', {'error_code': e.code, 'task_id': task.id}, status=500)


@permission_required('ipho_core.is_printstaff')
def bulk_print(request):
    messages = []

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

    queue_list = printer.allowed_choices(request.user)
    form = PrintDocsForm(request.POST or None, queue_list=queue_list)
    if form.is_valid():
        opts = {
            'ColourModel': form.cleaned_data['color'],
            'Staple': form.cleaned_data['staple'],
            'Duplex': form.cleaned_data['duplex'],
        }
        tot_printed = 0
        for pk in request.POST.getlist('printouts[]', []):
            d = get_or_none(Document, pk=pk)
            if d is not None:
                status = printer.send2queue(d.file, form.cleaned_data['queue'], user=request.user, user_opts=opts)
                tot_printed += 1
                l = PrintLog(document=d, type='P')
                l.save()
        for pk in request.POST.getlist('scans[]', []):
            d = get_or_none(Document, pk=pk)
            if d is not None:
                status = printer.send2queue(d.scan_file, form.cleaned_data['queue'], user=request.user, user_opts=opts)
                tot_printed += 1
                l = PrintLog(document=d, type='S')
                l.save()
        messages.append((
            'alert-success',
            '<strong>Success</strong> {} print job submitted. Please pickup your document at the printing station.'.
            format(tot_printed)
        ))

    all_docs = Document.objects.filter(
        student__delegation=filter_dg,
        exam=filter_ex,
        exam__delegation_status__action=ExamAction.TRANSLATION,
        exam__delegation_status__delegation=F('student__delegation'),
        exam__delegation_status__status=ExamAction.SUBMITTED
    ).annotate(
        last_print_p=Max(Case(When(printlog__type='P', then=F('printlog__timestamp')))),
        last_print_s=Max(Case(When(printlog__type='S', then=F('printlog__timestamp')))),
    ).values(
        'pk', 'exam__name', 'exam__id', 'position', 'student__delegation__name', 'student__code', 'student__id',
        'num_pages', 'barcode_base', 'barcode_num_pages', 'extra_num_pages', 'scan_file', 'scan_status',
        'scan_file_orig', 'scan_msg', 'last_print_p', 'last_print_s'
    ).order_by('student_id', 'position')

    paginator = Paginator(all_docs, 50)

    page = request.GET.get('page')
    try:
        docs_list = paginator.page(page)
    except PageNotAnInteger:
        docs_list = paginator.page(1)
    except EmptyPage:
        docs_list = paginator.page(paginator.num_pages)

    class url_builder(object):
        def __init__(self, base_url, get={}):
            self.url = base_url
            self.get = get

        def __call__(self, **kwargs):
            qdict = QueryDict('', mutable=True)
            for k, v in list(self.get.items()):
                qdict[k] = v
            for k, v in list(kwargs.items()):
                if v is None:
                    if k in qdict: del qdict[k]
                else:
                    qdict[k] = v
            url = self.url + '?' + qdict.urlencode()
            return url

    return render(
        request, 'ipho_exam/bulk_print.html', {
            'messages': messages,
            'exams': exams,
            'exam': exam,
            'delegations': delegations,
            'delegation': delegation,
            'queue_list': queue_list,
            'docs_list': docs_list,
            'scan_status_choices': Document.SCAN_STATUS_CHOICES,
            'all_pages': list(range(1, paginator.num_pages + 1)),
            'form': form,
            'this_url_builder': url_builder(reverse('exam:bulk-print'), request.GET),
        }
    )


@permission_required('ipho_core.is_printstaff')
def print_doc(request, type, exam_id, position, student_id, queue):
    queue_list = printer.allowed_choices(request.user)
    if not queue in (q[0] for q in queue_list):
        raise HttpResponseForbidden('Print queue not allowed.')
    doc = get_object_or_404(Document, exam=exam_id, position=position, student=student_id)

    if type == 'P':
        status = printer.send2queue(doc.file, queue, user=request.user)
        l = PrintLog(document=doc, type='P')
        l.save()
    elif doc.scan_file:
        status = printer.send2queue(doc.scan_file, queue, user=request.user)
        l = PrintLog(document=doc, type='S')
        l.save()
    else:
        raise Http404('Document type `{}` not found.'.format(type))

    n = request.META.get('HTTP_REFERER', reverse('exam:bulk-print'))
    return HttpResponseRedirect(n)


@permission_required('ipho_core.is_printstaff')
def set_scan_status(request, doc_id, status):
    doc = get_object_or_404(Document, id=doc_id)
    doc.scan_status = status
    doc.save()
    return HttpResponseRedirect(reverse('exam:bulk-print'))


@permission_required('ipho_core.is_printstaff')
def set_scan_full(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    doc.scan_file = doc.scan_file_orig
    doc.save()
    n = request.META.get('HTTP_REFERER', reverse('exam:bulk-print'))
    return HttpResponseRedirect(n)


@permission_required('ipho_core.is_printstaff')
def upload_scan(request):
    messages = []
    form = ScanForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        doc = get_object_or_404(
            Document,
            exam=form.cleaned_data['question'].exam,
            position=form.cleaned_data['question'].position,
            student=form.cleaned_data['student']
        )
        doc.scan_file = form.cleaned_data['file']
        doc.save()
        messages.append(('alert-success', '<i class="fa fa-check"></i> Scan uploaded.'))
    return render(request, 'ipho_exam/upload_scan.html', {'form': form, 'messages': messages})


@permission_required('ipho_core.is_printstaff')
def extra_sheets(request, exam_id=None):
    if exam_id is None:
        exams = Exam.objects.filter(hidden=False)
        return render(request, 'ipho_exam/extra_sheets_select_exam.html', {'exams': exams})
    messages = []
    form = ExtraSheetForm(exam_id, request.POST or None, initial={'template': 'exam_blank.tex'})
    if form.is_valid():
        student = form.cleaned_data['student']
        question = form.cleaned_data['question']
        exam = question.exam
        position = question.position
        quantity = form.cleaned_data['quantity']
        template_name = form.cleaned_data['template']
        doc = get_object_or_404(Document, exam=exam, position=position, student=student)

        doc_pdf = question_utils.generate_extra_sheets(student, question, doc.extra_num_pages, quantity, template_name)

        doc.extra_num_pages += quantity
        doc.save()

        res = HttpResponse(doc_pdf, content_type="application/pdf")
        res['content-disposition'] = 'attachment; filename="{} {} Z.pdf"'.format(student.code, exam.code)
        return res

    return render(request, 'ipho_exam/extra_sheets.html', {'form': form, 'messages': messages})


@permission_required('ipho_core.is_staff')
def api_keys(request):
    return render(request, 'ipho_exam/api_keys.html', {
        'EXAM_TOOLS_API_KEYS': settings.EXAM_TOOLS_API_KEYS,
    })
