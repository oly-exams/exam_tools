# Exam Tools
#
# Copyright (C) 2014 - 2019 Oly Exams Team
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

from builtins import zip
from builtins import range
from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotModified, HttpResponseForbidden, JsonResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.template.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string
from django.db.models import Sum, F, Q

from django.forms import modelformset_factory, inlineformset_factory

import itertools
import decimal
import json
from collections import OrderedDict
from hashlib import md5

from django.conf import settings
from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, VersionNode, Document
from ipho_exam import qquery as qwquery
from ipho_exam import qml

from .models import MarkingMeta, Marking, MarkingAction
from .forms import ImportForm, PointsForm


OFFICIAL_LANGUAGE = getattr(settings, 'OFFICIAL_LANGUAGE', 1)
OFFICIAL_DELEGATION = getattr(settings, 'OFFICIAL_DELEGATION')


@permission_required('ipho_core.is_staff')
def import_exam(request):
    ctx = {}
    ctx['alerts'] = []
    form = ImportForm(request.POST or None)
    if form.is_valid():
        exam = form.cleaned_data['exam']
        num_tot = 0
        num_created = 0
        num_marking_tot = 0
        num_marking_created = 0
        for question in exam.question_set.filter(type=Question.ANSWER):
            for delegation in Delegation.objects.exclude(name=OFFICIAL_DELEGATION).all():
                MarkingAction.objects.get_or_create(question=question, delegation=delegation)
            qw = qwquery.latest_version(question_id=question.pk, lang_id=OFFICIAL_LANGUAGE)
            question_points = qml.question_points(qw.qml)
            for i, (name, points) in enumerate(question_points):
                mmeta, created = MarkingMeta.objects.update_or_create(
                    question=question, name=name, defaults={
                        'max_points': points,
                        'position': i
                    }
                )
                num_created += created
                num_tot += 1

                for student in Student.objects.all():
                    for version_id, version_name in list(Marking.MARKING_VERSIONS.items()):
                        marking, created = Marking.objects.get_or_create(
                            marking_meta=mmeta, student=student, version=version_id
                        )
                        num_marking_created += created
                        num_marking_tot += 1

        ctx['alerts'].append(
            '<div class="alert alert-success"><p><strong>Success.</strong></p><p>{} marking subquestion were imported.<p><ul><li>{} created</li><li>{} updated</li></ul><p>{} student marking created.</p><ul><li>{} student marking already found</li></ul></div>'.
            format(
                num_tot, num_created, num_tot - num_created, num_marking_created, num_marking_tot - num_marking_created
            )
        )
    ctx['form'] = form
    return render(request, 'ipho_marking/import_exam.html', ctx)


@permission_required('ipho_core.is_marker')
def summary(request):
    vid = request.GET.get('version', 'O')

    points_per_student = []
    students = Student.objects.all().values('id', 'code')
    for student in students:
        stud_points_list = Marking.objects.filter(
            version=vid, student=student['id']
        ).values('marking_meta__question').annotate(question_points=Sum('points')).values_list(
            'marking_meta__question',
            'question_points',
        ).order_by('marking_meta__question__exam', 'marking_meta__question__position')

        stud_exam_points_list = Marking.objects.filter(
            version=vid, student=student['id']
        ).values('marking_meta__question__exam').annotate(
            exam_points=Sum('points')
        ).values('exam_points').order_by('marking_meta__question__exam')
        stud_marking_action_list = MarkingAction.objects.filter(delegation__student__pk__contains=student['id']).values('status').order_by('question__exam', 'question__position')
        points_per_student.append((student, list(zip(stud_points_list, stud_marking_action_list)), stud_exam_points_list))

    questions = MarkingMeta.objects.all().values('question').annotate(question_points=Sum('max_points')).values(
        'question__exam__name', 'question__name', 'question_points'
    ).order_by('question__exam', 'question__position').distinct()

    exams = MarkingMeta.objects.all().values('question__exam').annotate(exam_points=Sum('max_points')).values(
        'question__exam__name', 'exam_points'
    ).order_by('question__exam', ).distinct()

    context = {
        'vid': vid,
        'version': Marking.MARKING_VERSIONS[vid],
        'all_versions': Marking.MARKING_VERSIONS,
        'questions': questions,
        'points_per_student': points_per_student,
        'exams': exams,
        'editable_status': [MarkingAction.OPEN, MarkingAction.SUBMITTED],
    }
    return render(request, 'ipho_marking/summary.html', context)


@permission_required('ipho_core.is_marker')
def staff_stud_detail(request, version, stud_id, question_id):
    ctx = {}
    ctx['msg'] = []

    if not request.user.has_perm('ipho_core.is_marker') or version != 'O':
        raise RuntimeError('You cannot modify these markings!')

    question = get_object_or_404(Question, id=question_id)
    student = get_object_or_404(Student, id=stud_id)
    marking_action = get_object_or_404(MarkingAction, delegation=student.delegation, question=question)
    if marking_action.status == MarkingAction.LOCKED or marking_action.status == MarkingAction.FINAL:
        raise RuntimeError('These markings are locked, you cannot modify them!')

    metas = MarkingMeta.objects.filter(question=question)
    FormSet = modelformset_factory(
        Marking, form=PointsForm, fields=['points'], extra=0, can_delete=False, can_order=False
    )
    form = FormSet(
        request.POST or None, queryset=Marking.objects.filter(marking_meta__in=metas, student=student, version=version)
    )
    if form.is_valid():
        form.save()
        ctx['msg'].append((
            'alert-success',
            '<strong>Succses.</strong> Points have been saved. <a href="{}#details" class="btn btn-default btn-xs">back to summary</a>'.
            format(reverse('marking:summary'))
        ))

    ctx['version'] = version
    ctx['version_display'] = Marking.MARKING_VERSIONS[version]
    ctx['student'] = student
    ctx['question'] = question
    ctx['exam'] = question.exam
    ctx['form'] = form
    return render(request, 'ipho_marking/staff_edit.html', ctx)


@permission_required('ipho_core.is_staff')
def export_with_total(request):
    return export(request, include_totals=True)


@permission_required('ipho_core.is_staff')
def export(request, include_totals=False):
    versions = request.GET.get('v', 'O,D,F').split(',')

    csv_rows = []
    title_row = ['Student', 'First_Name', 'Last_Name', 'Delegation', 'Version']
    mmeta = MarkingMeta.objects.all().order_by('question__exam', 'question__position', 'position')
    for m in mmeta:
        title_row.append('{} - {} ({})'.format(m.question.name, m.name, m.max_points))
    exams = Exam.objects.filter(hidden=False)
    questions = Question.objects.filter(exam__hidden=False, code='A').order_by('exam', 'position')
    if include_totals:
        for question in questions:

            title_row.append('Question Total: {} - {}'.format(question.exam.name, question.name))
        for exam in exams:
            title_row.append('Exam Total: {}'.format(exam.name))
        title_row.append('Student Total')

    csv_rows.append(title_row)

    for student in Student.objects.all():
        stud_markings = Marking.objects.filter(
            student=student
        )
        for version in versions:
            row = [student.code, student.first_name, student.last_name, student.delegation.name, version]
            markings = stud_markings.filter(
                version=version
            ).order_by('marking_meta__question__exam', 'marking_meta__question__position', 'marking_meta__position')
            points = markings.values_list('points', flat=True)
            for marking, meta in zip(markings, mmeta):
                assert marking.marking_meta == meta
            row += points
            if include_totals:
                for question in questions:
                    row.append(
                        _get_total(markings.filter(marking_meta__question=question).values_list('points', flat=True))
                    )
                for exam in exams:
                    row.append(_get_total(markings.filter(marking_meta__question__exam=exam)))
                # try:
                student_total = _get_total(markings)
                row.append(student_total)
            row = ['-' if v is None else v for v in row]
            csv_rows.append(row)

    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="markings.csv"'

    writer = csv.writer(response)
    writer.writerows(csv_rows)

    return response


def _get_total(filtered_markings):
    return filtered_markings.aggregate(total=Sum(F('points')))['total']


@permission_required('ipho_core.is_delegation')
def delegation_export(request, exam_id):
    delegation = Delegation.objects.get(members=request.user)

    all_versions = request.GET.get('v', 'O,D,F').split(',')

    # check if the delegation should see all versions
    exam = get_object_or_404(Exam, id=exam_id)
    if MarkingAction.exam_in_progress(delegation=delegation, exam=exam) and not settings.SHOW_OFFICIAL_MARKS_IMMEDIATELY:
        allowed_versions = ['D']
    else:
        allowed_versions = ['O', 'D', 'F']
    versions = [v for v in all_versions if v in allowed_versions]

    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="markings.csv"'

    writer = csv.writer(response)
    students = Student.objects.filter(delegation=delegation)

    row1 = ['Student']
    row2 = ['Version']
    for student in students:
        for version in versions:
            row1.append(student.code)
            row2.append(Marking.MARKING_VERSIONS[version])
    writer.writerow(row1)
    writer.writerow(row2)
    totals = [decimal.Decimal(0)] * (len(row1) - 1)

    mmeta = MarkingMeta.objects.all().order_by('question__exam', 'question__position', 'position')
    for m in mmeta:
        row = ['{} - {} ({})'.format(m.question.name, m.name, m.max_points)]
        i = 0
        for student in students:
            for version in versions:
                marking = Marking.objects.get(
                    student__delegation=delegation, marking_meta=m, student=student, version=version
                ).points
                row.append(marking)
                if marking is not None:
                    totals[i] += marking
                i += 1
        row = ['-' if v is None else v for v in row]
        writer.writerow(row)

    row = ['Total']
    writer.writerow(row + totals)

    return response


@permission_required('ipho_core.is_delegation')
def delegation_summary(request):
    delegation = Delegation.objects.get(members=request.user)

    exam_list = []
    for exam in Exam.objects.filter(marking_active=True, hidden=False).order_by('pk').all():
        answer_sheet_list = Question.objects.filter(exam=exam, type=Question.ANSWER).order_by('exam__pk', 'position')
        question_ctx = []
        for question in answer_sheet_list:
            res = {'name':question.name, 'pk':question.pk}
            actions = []
            marking_status = get_object_or_404(MarkingAction, delegation=delegation, question=question).status
            if marking_status == MarkingAction.OPEN:
                res['edit'] = True
                if settings.SHOW_OFFICIAL_MARKS_IMMEDIATELY:
                    res['view'] = True
                else:
                    res['view_tooltip'] = 'Official marks are shown once you submitted your marks for moderation.'
                    res['viewall_tooltip'] = res['view_tooltip']
                confirm_action = {'link': reverse('marking:delegation-confirm',args=(question.pk,)),
                                 'text': 'Submit marks for moderation',
                                 }
                if settings.ACCEPT_MARKS_BEFORE_MODERATION:
                    accept_action = {'link': reverse('marking:delegation-final-confirm', args=(question.pk,)),
                                    'text': 'Accept marks without moderation',
                                    }
                elif settings.SIGN_OFF_FINAL_MARKS:
                    accept_action = {'link':reverse('marking:delegation-final-confirm',args=(question.pk,)),
                                    'text':'Sign off marks',
                                    'disabled':True,
                                    'tooltip': 'You can only sign off marks after the moderation.'
                                    }
                else:
                    accept_action = None
                actions = [confirm_action, accept_action]
            elif marking_status == MarkingAction.SUBMITTED:
                res['view'] = True
                res['edit_tooltip'] = 'Marks already submitted. You cannot edit them anymore.'
                res['editall_tooltip'] = res['edit_tooltip']
                confirm_action = {'link': reverse('marking:delegation-confirm', args=(question.pk,)),
                                 'text': 'Submit marks for moderation',
                                 'disabled': True,
                                 'tooltip': 'Marks already submitted.',
                                 }
                if (not settings.SHOW_OFFICIAL_MARKS_IMMEDIATELY) and settings.ACCEPT_MARKS_BEFORE_MODERATION:
                    accept_action = {'link': reverse('marking:delegation-final-confirm', args=(question.pk,)),
                                    'text': 'Accept marks without moderation',
                                    }
                elif settings.SIGN_OFF_FINAL_MARKS:
                    accept_action = {'link': reverse('marking:delegation-final-confirm', args=(question.pk,)),
                                    'text': 'Sign off marks',
                                    'disabled': True,
                                    'tooltip': 'You can only sign off marks after the moderation.',
                                    }
                else:
                    accept_action = None
                actions = [confirm_action, accept_action]
            elif marking_status == MarkingAction.LOCKED:
                res['view'] = True
                res['edit_tooltip'] = 'Marks already submitted. You cannot edit them anymore.'
                res['editall_tooltip'] = res['edit_tooltip']
                confirm_action = {'link': reverse('marking:delegation-confirm', args=(question.pk,)),
                                 'text': 'Submit marks for moderation',
                                 'disabled': True,
                                 'tooltip': 'Marks already submitted.',
                                 }
                if settings.SIGN_OFF_FINAL_MARKS:
                    accept_action = {'link': reverse('marking:delegation-final-confirm', args=(question.pk,)),
                                    'text': 'Sign off marks',
                                    'class': 'btn-success',
                                    }
                else:
                    accept_action = None
                actions = [confirm_action, accept_action]
            else:
                res['view'] = True
                res['edit_tooltip'] = 'Marks are finalized. You cannot edit them anymore.'
                res['editall_tooltip'] = res['edit_tooltip']
                confirm_action = {'link': reverse('marking:delegation-confirm', args=(question.pk,)),
                                 'text': 'Submit marks for moderation',
                                 'disabled': True,
                                 'tooltip': 'Marks already submitted.',
                                 }
                if settings.SIGN_OFF_FINAL_MARKS:
                    accept_action = {'link': reverse('marking:delegation-final-confirm', args=(question.pk,)),
                                    'text': 'Sign off marks',
                                    'disabled': True,
                                    'tooltip': 'Marks are already finalized.',
                                    }
                else:
                    accept_action = None
                actions = [confirm_action, accept_action]
            res['actions'] = actions
            question_ctx.append(res)
        exam_ctxt = {'questions': question_ctx, 'name': exam.name, 'pk': exam.pk}
        exam_list.append(exam_ctxt)

    students = Student.objects.filter(delegation=delegation).values('id', 'pk', 'code', 'first_name', 'last_name')
    vid = 'F'
    points_per_student = []
    for student in students:
        # Exam points
        stud_exam_points_list = Marking.objects.filter(
            version=vid, student=student['id'], marking_meta__question__exam__hidden=False
        ).values('marking_meta__question__exam').annotate(
            exam_points=Sum('points')
        ).values('exam_points').order_by('marking_meta__question__exam')
        total = sum([
            st_points['exam_points'] for st_points in stud_exam_points_list if st_points['exam_points'] is not None
        ])
        points_per_student.append((student, stud_exam_points_list, total))

    active_exams = Exam.objects.filter(hidden=False, marking_active=True)
    scans_table_per_exam = []
    scan_show_exams = Exam.objects.filter(hidden=False, show_scans=True)
    for exam in scan_show_exams:
        questions = exam.question_set.filter(type=Question.ANSWER)
        scans_of_students = []
        for student in students:
            # Scans
            stud_exam_scans_list = Document.objects.filter(
                student=student['pk'], exam=exam, scan_status='S'
            ).exclude(position=0  # remove general instructions
                      ).order_by('position')

            scans_of_students.append((student, stud_exam_scans_list))

        scans_table_per_exam.append((exam, questions, scans_of_students))

    final_points_exams = MarkingMeta.objects.filter(question__exam__hidden=False
                                                    ).values('question__exam').annotate(exam_points=Sum('max_points')
                                                                                        ).values(
                                                                                            'question__exam__name',
                                                                                            'exam_points'
                                                                                        ).order_by('question__exam',
                                                                                                   ).distinct()

    ctx = {
        'delegation': delegation,
        'students': students,
        'exam_list': exam_list,
        'final_points_exams': final_points_exams,
        'points_per_student': points_per_student,
        'active_exams': active_exams,
        'scans_table_per_exam': scans_table_per_exam,
    }
    return render(request, 'ipho_marking/delegation_summary.html', ctx)


@permission_required('ipho_core.is_delegation')
def delegation_stud_edit(request, stud_id, question_id):
    delegation = Delegation.objects.get(members=request.user)
    student = get_object_or_404(Student, id=stud_id)
    if student.delegation != delegation:
        return HttpResponseForbidden('You do not have permission to access this student.')

    question = get_object_or_404(Question, id=question_id, exam__marking_active=True)
    version = 'D'

    ctx = {}
    ctx['msg'] = []
    ctx['student'] = student
    ctx['question'] = question
    ctx['exam'] = question.exam

    marking_action, _ = MarkingAction.objects.get_or_create(
        question=question, delegation=delegation
        )
    if not marking_action.in_progress():
        ctx['msg'].append((('alert-info'),
                           '<strong>Note:</strong> The points have been submitted, you can no longer edit them.'))
        return render(request, 'ipho_marking/delegation_detail.html', ctx)

    metas = MarkingMeta.objects.filter(question=question)
    FormSet = modelformset_factory(
        Marking, form=PointsForm, fields=['points'], extra=0, can_delete=False, can_order=False
    )
    form = FormSet(
        request.POST or None, queryset=Marking.objects.filter(marking_meta__in=metas, student=student, version=version)
    )
    if form.is_valid():
        form.save()
        students = delegation.student_set.all()
        stud_id_list = [str(s.id) for s in students]
        next_stud_index = stud_id_list.index(stud_id) + 1
        next_stud_button = ''
        if next_stud_index < len(stud_id_list):
            next_stud_id = stud_id_list[next_stud_index]
            next_stud_button = ' <a href="{}" class="btn btn-default btn-xs">next student</a> '.format(
                reverse(
                    'marking:delegation-stud-detail-edit', kwargs={
                        'stud_id': next_stud_id,
                        'question_id': question_id
                    }
                )
            )

        ctx['msg'].append((
            'alert-success', '<strong>Success.</strong> Points have been saved.' + next_stud_button +
            ' <a href="{}#details" class="btn btn-default btn-xs">back to summary</a> '.format(
                reverse('marking:delegation-summary')
            )
        ))

    documents = Document.objects.filter(student=student, exam=question.exam, position=question.position)

    ctx['form'] = form
    ctx['documents'] = documents
    return render(request, 'ipho_marking/delegation_detail.html', ctx)


@permission_required('ipho_core.is_delegation')
def delegation_edit_all(request, question_id):
    delegation = Delegation.objects.get(members=request.user)
    students = Student.objects.filter(delegation=delegation).order_by('code')

    question = get_object_or_404(Question, id=question_id, exam__marking_active=True)
    version = 'D'

    ctx = {}
    ctx['msg'] = []
    ctx['students'] = students
    ctx['question'] = question
    ctx['exam'] = question.exam

    marking_action, _ = MarkingAction.objects.get_or_create(
        question=question, delegation=delegation
        )
    if not marking_action.in_progress():
        ctx['msg'].append((('alert-info'),
                           '<strong>Note:</strong> The points have been submitted, you can no longer edit them.'))
        return render(request, 'ipho_marking/delegation_detail.html', ctx)

    metas = MarkingMeta.objects.filter(question=question).order_by('position')
    FormSet = modelformset_factory(
        Marking, form=PointsForm, fields=['points'], extra=0, can_delete=False, can_order=False
    )
    formset = FormSet(
        request.POST or None, queryset=Marking.objects.filter(
            marking_meta__in=metas, student__in=students, version=version
            ).order_by('marking_meta__position', 'student__code')
    )

    if formset.is_valid():
        formset.save()
        ctx['msg'].append((
            'alert-success',
            '<strong>Success.</strong> Points have been saved. <a href="{}#details" class="btn btn-default btn-xs">back to summary</a>'.
            format(reverse('marking:delegation-summary'))
        ))
    if formset.total_error_count() > 0:
        ctx['msg'].append((
            'alert-danger', '<strong>Error.</strong> The submission could not be completed. See below for the errors.'
        ))

    documents = Document.objects.filter(
        exam=question.exam, position=question.position, student__in=students
    ).order_by('student__code')

    ctx['documents'] = documents
    ctx['formset'] = formset
    return render(request, 'ipho_marking/delegation_detail_all.html', ctx)


@permission_required('ipho_core.is_delegation')
def delegation_stud_view(request, stud_id, question_id):
    delegation = Delegation.objects.get(members=request.user)
    student = get_object_or_404(Student, id=stud_id)
    if student.delegation != delegation:
        return HttpResponseForbidden('You do not have permission to access this student.')

    question = get_object_or_404(Question, id=question_id, exam__marking_active=True)
    versions = ['O', 'D', 'F']
    versions_display = [Marking.MARKING_VERSIONS[v] for v in versions]

    ctx = {}
    ctx['msg'] = []
    ctx['student'] = student
    ctx['question'] = question
    ctx['exam'] = question.exam
    ctx['versions_display'] = versions_display

    marking_action, _ = MarkingAction.objects.get_or_create(
        question=question, delegation=delegation
        )
    if marking_action.in_progress() and not settings.SHOW_OFFICIAL_MARKS_IMMEDIATELY:
        ctx['msg'].append(
            (('alert-info'),
             '<strong>Note:</strong> You can see the official points only when you confirmed your markings.')
        )
        return render(request, 'ipho_marking/delegation_detail.html', ctx)

    metas = MarkingMeta.objects.filter(question=question)
    markings = Marking.objects.filter(
        marking_meta__in=metas, student=student, version__in=versions
    ).order_by('marking_meta')
    grouped_markings = [(k, {kk: list(gg)
                             for kk, gg in itertools.groupby(g, key=lambda m: m.version)})
                        for k, g in itertools.groupby(markings, key=lambda m: m.marking_meta)]

    documents = Document.objects.filter(student=student, exam=question.exam, position=question.position)

    ctx['documents'] = documents
    ctx['markings'] = grouped_markings
    return render(request, 'ipho_marking/delegation_detail.html', ctx)


@permission_required('ipho_core.is_delegation')
def delegation_view_all(request, question_id):
    delegation = Delegation.objects.get(members=request.user)
    students = Student.objects.filter(delegation=delegation)

    question = get_object_or_404(Question, id=question_id, exam__marking_active=True)
    versions = ['O', 'D', 'F']
    versions_display = [Marking.MARKING_VERSIONS[v] for v in versions]

    ctx = {}
    ctx['msg'] = []
    ctx['question'] = question
    ctx['students'] = students
    ctx['exam'] = question.exam
    ctx['versions_display'] = versions_display

    marking_action, _ = MarkingAction.objects.get_or_create(
        question=question, delegation=delegation
        )
    if marking_action.in_progress() and not settings.SHOW_OFFICIAL_MARKS_IMMEDIATELY:
        ctx['msg'].append(
            (('alert-info'),
             '<strong>Note:</strong> You can see the official points only when you confirmed your markings.')
        )
        return render(request, 'ipho_marking/delegation_detail_all.html', ctx)

    metas = MarkingMeta.objects.filter(question=question)
    markings = Marking.objects.filter(
        marking_meta__in=metas, version__in=versions, student__in=students
    ).order_by('marking_meta')
    grouped_markings = [(
        meta, [(student, {mark.version: mark
                          for mark in list(student_group)}) for student, student_group in
               itertools.groupby(sorted(meta_group, key=lambda m: m.student.code), key=lambda m: m.student.code)]
    ) for meta, meta_group in itertools.groupby(markings, key=lambda m: m.marking_meta)]

    documents = Document.objects.filter(exam=question.exam, position=question.position, student__in=students)

    ctx['documents'] = documents
    ctx['markings'] = grouped_markings
    ctx['sums'] = [{
        version: sum(entry[1][student][1][version].points or 0 for entry in grouped_markings)
        for version in ['O', 'D', 'F']
    } for student in range(len(students))]
    return render(request, 'ipho_marking/delegation_detail_all.html', ctx)


@permission_required('ipho_core.is_delegation')
def delegation_confirm(request, question_id, final_confirmation=False):
    delegation = Delegation.objects.get(members=request.user)
    question = get_object_or_404(Question, id=question_id, exam__marking_active=True)
    form_error = ''

    marking_action, _ = MarkingAction.objects.get_or_create(question=question, delegation=delegation)

    if not final_confirmation and not marking_action.in_progress():
        # can only confirm open actions
        return HttpResponseRedirect(reverse('marking:delegation-summary'))
    if final_confirmation:
        if not settings.SIGN_OFF_FINAL_MARKS and marking_action.status == MarkingAction.LOCKED:
            # if sign off is deactivated, locked marks cannot (don't need to be) signed off
            return HttpResponseRedirect(reverse('marking:delegation-summary'))
        if not settings.ACCEPT_MARKS_BEFORE_MODERATION and not marking_action.status == MarkingAction.LOCKED:
            # if not settings.ACCEPT_MARKS_BEFORE_MODERATION only locked marks can be final-confirmed
            return HttpResponseRedirect(reverse('marking:delegation-summary'))
        if settings.ACCEPT_MARKS_BEFORE_MODERATION and settings.SHOW_OFFICIAL_MARKS_IMMEDIATELY and marking_action.status == MarkingAction.SUBMITTED:
            # if accept_... and show_... submitted marks need to proceed to moderation
            return HttpResponseRedirect(reverse('marking:delegation-summary'))
    if marking_action.status == MarkingAction.FINAL:
        # final marks cannot be confirmed in any case
        return HttpResponseRedirect(reverse('marking:delegation-summary'))

    if final_confirmation:
        vid = 'O'
        ptqueryset = Marking.objects.filter(marking_meta__question=question, student__delegation=delegation, version='O').order_by('pk').values_list('points')
        ptlist = [str(p[0]) for p in ptqueryset]
        ptstr = str(ptlist)
        checksum = md5(ptstr.encode('ascii')).hexdigest()
    else:
        vid = 'D'
        checksum = None
    #questions = Question.objects.filter(exam=exam, type=Question.ANSWER)
    metas_query = MarkingMeta.objects.filter(question=question).order_by('position')
    markings_query = Marking.objects.filter(
        student__delegation=delegation, marking_meta__in=metas_query, version=vid
    ).order_by('marking_meta__position', 'student')

    if any(m.points is None for m in markings_query):
        if final_confirmation and marking_action.status == MarkingAction.LOCKED: # if status is LOCKED, all final marks should be there.
            msg = 'Some final marks for {} are missing, please contact support!'.format(question.name)
        elif final_confirmation:# id status is OPEN or SUBMITTED, the orgainzer marks should be finished, but maybe aren't
            msg = 'Some marks for {} are missing, please wait for the organizers to submit all marks!'.format(question.name)
        else:
            msg = 'Some marks for {} are missing, please submit marks for all subquestions and students before confirming!'.format(question.name)

        # TODO: nicer error page
        return HttpResponseForbidden(msg)

    error_messages = []
    if request.POST:
        if 'agree-submit' in request.POST:
            if final_confirmation:
                if not 'checksum' in request.POST:
                    msg = 'Something went wrong (checksum missing), please contact support!'
                    return HttpResponseForbidden(msg)
                if request.POST['checksum'] != checksum:
                    error_msg = ('The marks for {} have been changed. '.format(question.name) +
                        'Please reload the page and check the marks again. ' +
                        '<a href="{}" class="btn btn-default btn-xs">Reload</a>'
                        .format(reverse('marking:delegation-final-confirm', args=(question_id, )))
                        )
                    error_messages.append(('alert-danger', error_msg))
                    checksum = 'none'
                else:
                    for off_mark in Marking.objects.filter(marking_meta__question=question, student__delegation=delegation, version='O'):
                        fin_mark, _ = Marking.objects.get_or_create(marking_meta=off_mark.marking_meta, student=off_mark.student, version='F')
                        fin_mark.points = off_mark.points
                        fin_mark.comment = off_mark.comment
                        fin_mark.save()
                    marking_action.status = MarkingAction.FINAL
                    marking_action.save()
                    return HttpResponseRedirect(reverse('marking:delegation-summary'))
            else:
                marking_action.status = MarkingAction.SUBMITTED
                marking_action.save()
                return HttpResponseRedirect(reverse('marking:delegation-summary'))
        elif 'reject-final' in request.POST and final_confirmation:
            # i.e. if delegation rejects final marks, unlock marking action
            marking_action.status = MarkingAction.SUBMITTED
            marking_action.save()
            return HttpResponseRedirect(reverse('marking:delegation-summary'))
        else:
            form_error = '<strong>Error:</strong> You have to confirm the marking before continuing.'

    metas = {k: list(g) for k, g in itertools.groupby(metas_query, key=lambda m: m.question.pk)}
    markings = {
        k: list(sorted(g, key=lambda m: m.student.pk))
        for k, g in itertools.groupby(markings_query, key=lambda m: m.marking_meta.question.pk)
    }
    #totals is of the form {question.pk:{student.pk:total, ...}, ...}
    totals_questions = {
        k: { #s is a list of markings for student p
            p: sum(m.points for m in s)
            for p, s in itertools.groupby(sorted(g, key=lambda m: m.student.pk), key=lambda m: m.student.pk)}
        for k, g in itertools.groupby(markings_query, key=lambda m: m.marking_meta.question.pk)
    }

    totals = {p: sum(totals_questions[k][p] for k in totals_questions) for p in list(totals_questions.values())[0]}

    ctx = {
        'exam': question.exam,
        'questions': (question,),
        'markings': markings,
        'metas': metas,
        'totals_questions': totals_questions,
        'totals': totals,
        'form_error': form_error,
        'error_messages': error_messages,
        'checksum': checksum,
    }
    if final_confirmation:
        ctx['confirmation_h2'] = 'Sign off final points for {}'.format(question.name)
        ctx['confirmation_info'] = (
            'Please check the points displayed below. ' +
            'Note that you <strong>cannot</strong> moderate the points if you acceppt them now.')
        ctx['confirmation_checkbox_label'] = 'I accept the final markings.'
        ctx['confirm_button_label'] = 'Accept'

        if  marking_action.status == MarkingAction.LOCKED:
            # i.e. if moderation has happened
            ctx['confirmation_info'] = (
                'Please check the points displayed below. ' +
                'If the points are not as discussed in the moderation, ' +
                'you can reopen it to allow the organizers to change the marks. ' +
                'Note that this does <strong>not</strong> lead to another moderation session.')
            ctx['confirmation_alert_class'] = 'alert-info'
            ctx['reject_button_label'] = 'Reopen moderation'
        else:
            ctx['confirmation_alert_class'] = 'alert-warning'

    else:
        ctx['confirmation_h2'] = 'Confirm points for {}'.format(question.name)
        ctx['confirmation_info'] = 'You need to confirm the marking of your delegation before you can see the points assigned by the official markers.'
        ctx['confirmation_checkbox_label'] = 'I confirm my version of the markings.'
        ctx['confirm_button_label'] = 'Confirm'
    return render(request, 'ipho_marking/delegation_confirm.html', ctx)


@permission_required('ipho_core.is_marker')
def moderation_index(request, question_id=None):
    questions = Question.objects.filter(
        exam__hidden=False, exam__moderation_active=True, type=Question.ANSWER
    ).order_by('exam__code', 'position')
    question = None if question_id is None else get_object_or_404(Question, id=question_id)
    if question is not None:
        free_actions = MarkingAction.objects.filter(question=question).filter(Q(status=MarkingAction.OPEN)|Q(status=MarkingAction.SUBMITTED)).values('delegation_id')
        delegations = Delegation.objects.filter(id__in=free_actions).all()
    else:
        delegations = Delegation.objects.all()
    ctx = {'questions': questions, 'question': question, 'delegations': delegations}
    return render(request, 'ipho_marking/moderation_index.html', ctx)


@permission_required('ipho_core.is_marker')
def moderation_detail(request, question_id, delegation_id):
    question = get_object_or_404(Question, id=question_id, exam__hidden=False, exam__moderation_active=True)
    delegation = get_object_or_404(Delegation, id=delegation_id)

    marking_action = get_object_or_404(MarkingAction, delegation=delegation, question=question)
    if marking_action.status == MarkingAction.LOCKED or marking_action.status == MarkingAction.FINAL:
        raise RuntimeError('These markings are locked, you cannot modify them!')

    metas = MarkingMeta.objects.filter(question=question)
    students = delegation.student_set.all()

    student_forms = []
    marking_forms = []
    all_valid = True
    with_errors = False
    for i, student in enumerate(students):
        markings_official = Marking.objects.filter(
            student=student, marking_meta__in=metas, version='O'
        ).order_by('marking_meta__position')
        markings_delegation = Marking.objects.filter(
            student=student, marking_meta__in=metas, version='D'
        ).order_by('marking_meta__position')

        FormSet = modelformset_factory(
            Marking, form=PointsForm, fields=['points'], extra=0, can_delete=False, can_order=False
        )
        form = FormSet(
            request.POST or None,
            prefix='Stud-{}'.format(student.pk),
            queryset=Marking.objects.filter(marking_meta__in=metas, student=student, version='F')
        )
        for j, f in enumerate(form):
            f.fields['points'].widget.attrs['tabindex'] = i * len(metas) + j + 1
            f.fields['points'].widget.attrs['style'] = 'width:60px'

        # TODO: accept only submission without None
        all_valid = all_valid and form.is_valid()
        with_errors = with_errors or form.errors

        student_forms.append((
            student, form, markings_official,
            sum((m.points for m in markings_official if m.points is not None), decimal.Decimal(0)),
            sum((m.points for m in markings_delegation if m.points is not None), decimal.Decimal(0))
        ))
        marking_forms.append(zip(markings_official, markings_delegation, form))

    if all_valid:
        for _, form, _, _, _ in student_forms:
            form.save()
        if settings.SIGN_OFF_FINAL_MARKS:
            marking_action.status = MarkingAction.LOCKED
        else:
            # if sign off is deactivated, jump directly to locked (note that this also locks the moderation!)
            marking_action.status = MarkingAction.FINAL
        marking_action.save()
        return HttpResponseRedirect(
            reverse(
                'marking:moderation-confirmed', kwargs={
                    'question_id': question.pk,
                    'delegation_id': delegation.pk
                }
            )
        )
    # TODO: display errors
    ctx = {
        'question': question,
        'delegation': delegation,
        'student_forms': student_forms,
        'marking_forms': list(zip(metas, zip(*marking_forms))),
        'request': request,
        'max_points_sum': sum(m.max_points for m in metas)
    }
    return render(request, 'ipho_marking/moderation_detail.html', ctx)


@permission_required('ipho_core.is_marker')
def official_marking_index(request, question_id=None):
    questions = Question.objects.filter(exam__hidden=False, type=Question.ANSWER).order_by('exam__code', 'position')
    question = None if question_id is None else get_object_or_404(Question, id=question_id)
    if question is not None:
        free_actions = MarkingAction.objects.filter(question=question).filter(Q(status=MarkingAction.OPEN)|Q(status=MarkingAction.SUBMITTED)).values('delegation_id')
        delegations = Delegation.objects.filter(id__in=free_actions).all()
    else:
        delegations = Delegation.objects.all()
    ctx = {'questions': questions, 'question': question, 'delegations': delegations}
    return render(request, 'ipho_marking/official_marking_index.html', ctx)


@permission_required('ipho_core.is_marker')
def official_marking_detail(request, question_id, delegation_id):
    question = get_object_or_404(Question, id=question_id, exam__hidden=False)
    delegation = get_object_or_404(Delegation, id=delegation_id)
    marking_action = get_object_or_404(MarkingAction, delegation=delegation, question=question)
    if marking_action.status == MarkingAction.LOCKED or marking_action.status == MarkingAction.FINAL:
        raise RuntimeError('These markings are locked, you cannot modify them!')

    metas = MarkingMeta.objects.filter(question=question)
    students = delegation.student_set.all()

    student_forms = []
    all_valid = True
    with_errors = False
    for i, student in enumerate(students):
        FormSet = modelformset_factory(
            Marking, form=PointsForm, fields=['points'], extra=0, can_delete=False, can_order=False
        )
        form = FormSet(
            request.POST or None,
            prefix='Stud-{}'.format(student.pk),
            queryset=Marking.objects.filter(marking_meta__in=metas, student=student, version='O')
        )
        for j, f in enumerate(form):
            f.fields['points'].widget.attrs['tabindex'] = i * len(metas) + j + 1
            f.fields['points'].widget.attrs['style'] = 'width:100px'

        # TODO: accept only submission without None
        all_valid = all_valid and form.is_valid()
        with_errors = with_errors or form.errors

        student_forms.append((student, form))

    if all_valid:
        for _, form in student_forms:
            form.save()
        return HttpResponseRedirect(
            reverse(
                'marking:official-marking-confirmed',
                kwargs={
                    'question_id': question.pk,
                    'delegation_id': delegation.pk
                }
            )
        )
    # TODO: display errors
    ctx = {
        'question': question,
        'delegation': delegation,
        'student_forms': student_forms,
        'marking_forms': list(zip(metas, zip(*(f[1] for f in student_forms)))),
        'request': request,
        'max_points_sum': sum(m.max_points for m in metas)
    }
    return render(request, 'ipho_marking/official_marking_detail.html', ctx)


@permission_required('ipho_core.is_marker')
def official_marking_confirmed(request, question_id, delegation_id):
    question = get_object_or_404(Question, id=question_id, exam__hidden=False)
    delegation = get_object_or_404(Delegation, id=delegation_id)

    markings = Marking.objects.filter(
        marking_meta__question=question, version='O', student__delegation=delegation
    ).values('student').annotate(total=Sum('points')).order_by('student').values(
        'student__first_name', 'student__last_name', 'student__code', 'total'
    )

    ctx = {'question': question, 'delegation': delegation, 'markings': markings}
    return render(request, 'ipho_marking/official_marking_confirmed.html', ctx)


@permission_required('ipho_core.is_marker')
def moderation_confirmed(request, question_id, delegation_id):
    question = get_object_or_404(Question, id=question_id, exam__hidden=False, exam__moderation_active=True)
    delegation = get_object_or_404(Delegation, id=delegation_id)

    markings = Marking.objects.filter(
        marking_meta__question=question, version='F', student__delegation=delegation
    ).values('student').annotate(total=Sum('points')).order_by('student').values(
        'student__first_name', 'student__last_name', 'student__code', 'total'
    )

    ctx = {'question': question, 'delegation': delegation, 'markings': markings}
    return render(request, 'ipho_marking/moderation_confirmed.html', ctx)


@permission_required('ipho_core.is_staff')
def marking_submissions(request):
    ctx = {
        "summaries": [(
            question.name,
            MarkingAction.objects.filter(question=question, status=MarkingAction.OPEN
                                      ).exclude(delegation__name=OFFICIAL_DELEGATION).count(),
            MarkingAction.objects.filter(question=question, status=MarkingAction.SUBMITTED
                                      ).exclude(delegation__name=OFFICIAL_DELEGATION).count(),
            MarkingAction.objects.filter(question=question, status=MarkingAction.OPEN
                                      ).exclude(delegation__name=OFFICIAL_DELEGATION).values_list(
                                          'delegation__country', flat=True
                                      ),
            MarkingAction.objects.filter(question=question, status=MarkingAction.LOCKED
                                      ).exclude(delegation__name=OFFICIAL_DELEGATION).count(),
            MarkingAction.objects.filter(question=question, status=MarkingAction.FINAL
                                      ).exclude(delegation__name=OFFICIAL_DELEGATION).count(),
            MarkingAction.objects.filter(question=question
                                      ).exclude( status=MarkingAction.FINAL, delegation__name=OFFICIAL_DELEGATION
                                      ).values_list(
                                          'delegation__country', flat=True
                                      ),
        ) for question in Question.objects.filter(exam__marking_active=True, type=Question.ANSWER)]
    }
    return render(request, 'ipho_marking/marking_submissions.html', ctx)


def progress(request):
    vid = request.GET.get('version', 'O')
    if request.user.has_perm('ipho_core.is_staff'):
        all_versions = Marking.MARKING_VERSIONS
    elif request.user.has_perm('ipho_core.is_marker'):
        all_versions = OrderedDict([(k, v) for k, v in list(Marking.MARKING_VERSIONS.items()) if k != 'D'])
        if vid not in all_versions:
            return HttpResponseForbidden('Only the staff can see this page.')
    else:
        return HttpResponseForbidden('You do not have permission to access this page.')

    students = Student.objects.all().values('id', 'code')

    marking_statuses = []
    for exam in Exam.objects.all():
        questions = Question.objects.filter(exam=exam, type=Question.ANSWER)
        metas_groups = [MarkingMeta.objects.filter(question=question) for question in questions]
        added = False
        for student in students:
            statuses = []
            for question, metas in zip(questions, metas_groups):
                markings = Marking.objects.filter(
                    version=vid,
                    student=student['id'],
                    marking_meta__question=question,
                    points__isnull=False,
                )
                statuses.append(markings.count() < metas.count())
            if any(statuses):
                if not added:
                    marking_statuses.append([exam.name, questions, []])
                    added = True
                marking_statuses[-1][2].append((student['code'], statuses))

    ctx = {
        'version': Marking.MARKING_VERSIONS[vid],
        'all_versions': all_versions,
        'marking_statuses': marking_statuses,
    }
    return render(request, 'ipho_marking/progress.html', ctx)
