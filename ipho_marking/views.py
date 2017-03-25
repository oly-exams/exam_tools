# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
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

from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotModified, HttpResponseForbidden, JsonResponse, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.core.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string
from django.db.models import Sum

from django.forms import modelformset_factory, inlineformset_factory

import itertools

from django.conf import settings
from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, VersionNode, ExamAction, Document
from ipho_exam import qquery as qwquery
from ipho_exam import qml

from .models import MarkingMeta, Marking
from .forms import ImportForm, PointsForm

OFFICIAL_LANGUAGE = getattr(settings, 'OFFICIAL_LANGUAGE', 1)

@permission_required('ipho_core.is_staff')
def import_exam(request):
    ctx={}
    ctx['alerts'] = []
    form = ImportForm(request.POST or None)
    if form.is_valid():
        exam = form.cleaned_data['exam']
        num_tot = 0
        num_created = 0
        num_marking_tot = 0
        num_marking_created = 0
        for question in exam.question_set.filter(type=Question.ANSWER):
            qw = qwquery.latest_version(question_id=question.pk, lang_id=OFFICIAL_LANGUAGE)
            question_points = qml.question_points(qw.qml)
            for i,(name, points) in enumerate(question_points):
                mmeta, created = MarkingMeta.objects.update_or_create(question=question, name=name,
                    defaults={'max_points': points, 'position': i})
                num_created += created
                num_tot += 1

                for student in Student.objects.all():
                    for version_id, version_name in Marking.MARKING_VERSIONS.iteritems():
                        marking, created = Marking.objects.get_or_create(marking_meta=mmeta, student=student, version=version_id)
                        num_marking_created += created
                        num_marking_tot += 1

        ctx['alerts'].append('<div class="alert alert-success"><strong>Success.</strong> {} marking subquestion were imported.<ul><li> {} created</li><li>{} updated</li><li>{} student marking created</li><li>{} student marking already found</li>.</div>'.format(num_tot, num_created, num_tot-num_created, num_marking_created, num_marking_tot-num_marking_created))
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
        ).values(
            'marking_meta__question'
        ).annotate(
            question_points=Sum('points')
        ).values_list(
            'marking_meta__question',
            'question_points',
        ).order_by('marking_meta__question__exam','marking_meta__question__position')

        stud_exam_points_list = Marking.objects.filter(
            version=vid, student=student['id']
        ).values(
            'marking_meta__question__exam'
        ).annotate(
            exam_points=Sum('points')
        ).values(
            'exam_points'
        ).order_by(
            'marking_meta__question__exam'
        )

        points_per_student.append( (student, stud_points_list, stud_exam_points_list) )

    questions = MarkingMeta.objects.all().values(
        'question'
    ).annotate(
        question_points=Sum('max_points')
    ).values(
        'question__exam__name',
        'question__name',
        'question_points'
    ).order_by(
        'question__exam',
        'question__position'
    ).distinct()

    exams = MarkingMeta.objects.all().values(
        'question__exam'
    ).annotate(
        exam_points=Sum('max_points')
    ).values(
        'question__exam__name',
        'exam_points'
    ).order_by(
        'question__exam',
    ).distinct()

    context = {
        'vid': vid,
        'version': Marking.MARKING_VERSIONS[vid],
        'all_versions': Marking.MARKING_VERSIONS,
        'questions': questions,
        'points_per_student': points_per_student,
        'exams': exams,
    }
    return render(request, 'ipho_marking/summary.html', context)

@permission_required('ipho_core.is_marker')
def staff_stud_detail(request, version, stud_id, question_id):
    ctx = RequestContext(request)
    ctx['msg'] = []

    if not request.user.has_perm('ipho_core.is_marker') and version != 'O':
        raise RuntimeError('You cannot modify these markings!')

    question = get_object_or_404(Question, id=question_id)
    student = get_object_or_404(Student, id=stud_id)

    metas = MarkingMeta.objects.filter(question=question)
    FormSet = modelformset_factory(Marking, form=PointsForm, fields=['points'], extra=0, can_delete=False, can_order=False)
    form = FormSet(request.POST or None, queryset=Marking.objects.filter(marking_meta=metas, student=student, version=version))
    if form.is_valid():
        form.save()
        ctx['msg'].append( ('alert-success', '<strong>Succses.</strong> Points have been saved. <a href="{}" class="btn btn-default btn-xs">back to summary</a>'.format(reverse('marking:summary'))) )

    ctx['version'] = version
    ctx['version_display'] = Marking.MARKING_VERSIONS[version]
    ctx['student'] = student
    ctx['question'] = question
    ctx['exam'] = question.exam
    ctx['form'] = form
    return render(request, 'ipho_marking/staff_edit.html', ctx)

@permission_required('ipho_core.is_marker')
def export(request):
    versions = request.GET.get('v', 'O,D,F').split(',')
    exam_id = request.GET.get('exam', False)

    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="markings.csv"'

    writer = csv.writer(response)
    title_row = ['Student', 'Delegation', 'Version']
    mmeta = MarkingMeta.objects.all().order_by('question__exam', 'question__position', 'position')
    for m in mmeta:
        title_row.append( '{} - {} ({})'.format(m.question.name, m.name, m.max_points) )
    writer.writerow(title_row)

    for student in Student.objects.all():
        for version in versions:
            row = [student.code, student.delegation.name, version]
            markings = Marking.objects.filter(student=student, version=version).order_by('marking_meta__question__exam', 'marking_meta__question__position', 'marking_meta__position').values_list('points', flat=True)
            row += markings
            row = map(lambda v: '-' if v is None else v, row)
            writer.writerow(row)

    return response

@permission_required('ipho_core.is_delegation')
def delegation_export(request, exam_id):
    versions = request.GET.get('v', 'O,D,F').split(',')
    delegation = Delegation.objects.get(members=request.user)

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
    totals = [0.0]*(len(row1) - 1)

    mmeta = MarkingMeta.objects.all().order_by('question__exam', 'question__position', 'position')
    for m in mmeta:
        row = ['{} - {} ({})'.format(m.question.name, m.name, m.max_points)]
        i = 0
        for student in students:
            for version in versions:
                marking = Marking.objects.get(student__delegation=delegation, marking_meta=m, student=student, version=version).points
                row.append(marking)
                if marking is not None:
                    totals[i] += marking
                i += 1
        row = map(lambda v: '-' if v is None else v, row)
        writer.writerow(row)

    row = ['Total']
    totals = [round(t, 1) for t in totals]
    writer.writerow(row + totals)

    return response

@permission_required('ipho_core.is_delegation')
def delegation_summary(request):
    delegation = Delegation.objects.get(members=request.user)
    points_submissions = ExamAction.objects.filter(delegation=delegation, action=ExamAction.POINTS, exam__marking_active=True).order_by('exam')
    students = Student.objects.filter(delegation=delegation).values('id', 'pk', 'code', 'first_name', 'last_name')
    vid = 'F'
    points_per_student = []
    for student in students:
        stud_exam_points_list = Marking.objects.filter(
            version=vid, student=student['id']
        ).values(
            'marking_meta__question__exam'
        ).annotate(
            exam_points=Sum('points')
        ).values(
            'exam_points'
        ).order_by(
            'marking_meta__question__exam'
        )
        total = sum([ st_points['exam_points'] for st_points in stud_exam_points_list if st_points['exam_points'] is not None ])
        points_per_student.append( (student, stud_exam_points_list, total) )

    exams = MarkingMeta.objects.filter(question__exam__hidden=False).values(
        'question__exam'
    ).annotate(
        exam_points=Sum('max_points')
    ).values(
        'question__exam__name',
        'exam_points'
    ).order_by(
        'question__exam',
    ).distinct()

    ctx = {
        'delegation': delegation,
        'students': students,
        'points_submissions': points_submissions,
        'exams': exams,
        'points_per_student': points_per_student,
        'OPEN_STATUS': ExamAction.OPEN,
        'SUBMITTED_STATUS': ExamAction.SUBMITTED,
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

    ctx = RequestContext(request)
    ctx['msg'] = []
    ctx['student'] = student
    ctx['question'] = question
    ctx['exam'] = question.exam

    points_submissions,_ = ExamAction.objects.get_or_create(exam=question.exam, delegation=delegation, action=ExamAction.POINTS)
    if points_submissions.status == ExamAction.SUBMITTED:
        ctx['msg'].append( (('alert-info'), '<strong>Note:</strong> The points have been submitted, you can no longer edit them.') )
        return render(request, 'ipho_marking/delegation_detail.html', ctx)

    metas = MarkingMeta.objects.filter(question=question)
    FormSet = modelformset_factory(Marking, form=PointsForm, fields=['points'], extra=0, can_delete=False, can_order=False)
    form = FormSet(request.POST or None, queryset=Marking.objects.filter(marking_meta=metas, student=student, version=version))
    if form.is_valid():
        form.save()
        ctx['msg'].append( ('alert-success', '<strong>Success.</strong> Points have been saved. <a href="{}" class="btn btn-default btn-xs">back to summary</a>'.format(reverse('marking:delegation-summary'))) )

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

    ctx = RequestContext(request)
    ctx['msg'] = []
    ctx['students'] = students
    ctx['question'] = question
    ctx['exam'] = question.exam

    points_submissions, _ = ExamAction.objects.get_or_create(exam=question.exam, delegation=delegation, action=ExamAction.POINTS)
    if points_submissions.status == ExamAction.SUBMITTED:
        ctx['msg'].append( (('alert-info'), '<strong>Note:</strong> The points have been submitted, you can no longer edit them.') )
        return render(request, 'ipho_marking/delegation_detail.html', ctx)

    metas = MarkingMeta.objects.filter(question=question).order_by('position')
    FormSet = modelformset_factory(Marking, form=PointsForm, fields=['points'], extra=0, can_delete=False, can_order=False)
    formset = FormSet(request.POST or None, queryset=Marking.objects.filter(marking_meta=metas, student=students, version=version))

    if formset.is_valid():
        formset.save()
        ctx['msg'].append( ('alert-success', '<strong>Success.</strong> Points have been saved. <a href="{}" class="btn btn-default btn-xs">back to summary</a>'.format(reverse('marking:delegation-summary'))) )
    if formset.total_error_count() > 0:
        ctx['msg'].append( ('alert-danger', '<strong>Error.</strong> The submission could not be completed. See below for the errors.'.format(reverse('marking:delegation-summary'))) )
    
    documents = Document.objects.filter(exam=question.exam, position=question.position, student=students).order_by('student__code')

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

    ctx = RequestContext(request)
    ctx['msg'] = []
    ctx['student'] = student
    ctx['question'] = question
    ctx['exam'] = question.exam
    ctx['versions_display'] = versions_display

    points_submissions,_ = ExamAction.objects.get_or_create(exam=question.exam, delegation=delegation, action=ExamAction.POINTS)
    if points_submissions.status == ExamAction.OPEN:
        ctx['msg'].append( (('alert-info'), '<strong>Note:</strong> You can see the official points only when you confirmed your markings.') )
        return render(request, 'ipho_marking/delegation_detail.html', ctx)

    metas = MarkingMeta.objects.filter(question=question)
    markings = Marking.objects.filter(marking_meta=metas, student=student, version__in=versions).order_by('marking_meta')
    grouped_markings = [
        (
            k,
            {kk: list(gg) for kk,gg in itertools.groupby(g, key=lambda m: m.version)}
        )
        for k,g in itertools.groupby(markings, key=lambda m: m.marking_meta)
    ]

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

    ctx = RequestContext(request)
    ctx['msg'] = []
    ctx['question'] = question
    ctx['students'] = students
    ctx['exam'] = question.exam
    ctx['versions_display'] = versions_display

    points_submissions,_ = ExamAction.objects.get_or_create(exam=question.exam, delegation=delegation, action=ExamAction.POINTS)
    if points_submissions.status == ExamAction.OPEN:
        ctx['msg'].append( (('alert-info'), '<strong>Note:</strong> You can see the official points only when you confirmed your markings.') )
        return render(request, 'ipho_marking/delegation_detail_all.html', ctx)

    metas = MarkingMeta.objects.filter(question=question)
    markings = Marking.objects.filter(marking_meta=metas, version__in=versions, student=students).order_by('marking_meta')
    grouped_markings = [
        (
            meta,
            [   
                (
                    student, 
                    {mark.version: mark for mark in list(student_group)}
                )
                for student, student_group in itertools.groupby(sorted(meta_group, key=lambda m: m.student.code), key=lambda m: m.student.code)
            ]
        )
        for meta, meta_group in itertools.groupby(markings, key=lambda m: m.marking_meta)
    ]

    documents = Document.objects.filter(exam=question.exam, position=question.position, student=students)

    ctx['documents'] = documents
    ctx['markings'] = grouped_markings
    ctx['sums'] = [
        {version: sum(entry[1][student][1][version].points or 0 for entry in grouped_markings) for version in ['O', 'D', 'F']}
        for student in range(len(students))
    ]
    return render(request, 'ipho_marking/delegation_detail_all.html', ctx)

@permission_required('ipho_core.is_delegation')
def delegation_confirm(request, exam_id):
    delegation = Delegation.objects.get(members=request.user)
    exam = get_object_or_404(Exam, id=exam_id, marking_active=True)
    form_error = ''

    points_submissions,_ = ExamAction.objects.get_or_create(exam=exam, delegation=delegation, action=ExamAction.POINTS)
    if points_submissions.status == ExamAction.SUBMITTED:
        return HttpResponseRedirect(reverse('marking:delegation-summary'))

    if request.POST:
        if 'agree-submit' in request.POST:
            points_submissions.status = ExamAction.SUBMITTED
            points_submissions.save()
            return HttpResponseRedirect(reverse('marking:delegation-summary'))
        else:
            form_error = '<strong>Error:</strong> You have to confirm the marking before continuing.'

    questions = Question.objects.filter(exam=exam, type=Question.ANSWER)
    metas_query = MarkingMeta.objects.filter(question=questions).order_by('question','position')
    markings_query = Marking.objects.filter(student__delegation=delegation, marking_meta=metas_query, version='D').order_by('marking_meta__question', 'marking_meta__position','student')
    metas = {k: list(g) for k,g in itertools.groupby(metas_query, key=lambda m: m.question.pk)}
    markings = {k: list(sorted(g, key=lambda m: m.student.pk)) for k,g in itertools.groupby(markings_query, key=lambda m: m.marking_meta.question.pk)}
    ctx = {'exam': exam, 'questions': questions, 'markings': markings, 'metas': metas, 'form_error': form_error}
    return render(request, 'ipho_marking/delegation_confirm.html', ctx)


@permission_required('ipho_core.is_marker')
def moderation_index(request, question_id=None):
    questions = Question.objects.filter(exam__hidden=False, type=Question.ANSWER).order_by('exam__code', 'position')
    question = None if question_id is None else get_object_or_404(Question, id=question_id)
    delegations = Delegation.objects.all()
    ctx={'questions': questions, 'question': question, 'delegations': delegations}
    return render(request, 'ipho_marking/moderation_index.html', ctx)

@permission_required('ipho_core.is_marker')
def moderation_detail(request, question_id, delegation_id):
    question = get_object_or_404(Question, id=question_id)
    delegation = get_object_or_404(Delegation, id=delegation_id)

    metas = MarkingMeta.objects.filter(question=question)

    student_forms = []
    all_valid = True
    with_errors = False
    for student in delegation.student_set.all():
        markings_official = Marking.objects.filter(student=student, marking_meta=metas, version='O').order_by('marking_meta__position')
        markings_delegation = Marking.objects.filter(student=student, marking_meta=metas, version='D').order_by('marking_meta__position')

        FormSet = modelformset_factory(Marking, form=PointsForm, fields=['points'], extra=0, can_delete=False, can_order=False)
        form = FormSet(request.POST or None, prefix='Stud-{}'.format(student.pk), queryset=Marking.objects.filter(marking_meta=metas, student=student, version='F'))

        # TODO: accept only submission without None
        all_valid = all_valid and form.is_valid()
        with_errors = with_errors or form.errors

        student_forms.append((student, markings_official, markings_delegation, form))

    if all_valid:
        for _, _, _, form in student_forms:
            form.save()
        return HttpResponseRedirect(reverse('marking:moderation-confirmed', kwargs={'question_id':question.pk, 'delegation_id':delegation.pk}))
    # TODO: display errors
    ctx = {'metas': metas, 'question': question, 'delegation': delegation, 'student_forms': student_forms}
    return render(request, 'ipho_marking/moderation_detail.html', ctx)

@permission_required('ipho_core.is_marker')
def moderation_confirmed(request, question_id, delegation_id):
    question = get_object_or_404(Question, id=question_id)
    delegation = get_object_or_404(Delegation, id=delegation_id)

    markings = Marking.objects.filter( marking_meta__question=question, version='F', student__delegation=delegation).values('student').annotate(total=Sum('points')).order_by('student').values('student__first_name', 'student__last_name', 'student__code', 'total')

    ctx = {'question': question, 'delegation': delegation, 'markings': markings}
    return render(request, 'ipho_marking/moderation_confirmed.html', ctx)


@permission_required('ipho_core.is_staff')
def submission_summary(request):
    ctx = {
        "summaries":[
            (
                exam.name,
                ExamAction.objects.filter(exam=exam, action=ExamAction.POINTS,
                    status=ExamAction.OPEN).count() - 1,
                ExamAction.objects.filter(exam=exam, action=ExamAction.POINTS,
                    status=ExamAction.SUBMITTED).count(),
                ExamAction.objects.filter(exam=exam, action=ExamAction.POINTS,
                    status=ExamAction.OPEN).values('delegation__country'),
            )
            for exam in Exam.objects.filter(marking_active=True)
        ]
    }
    return render(request, 'ipho_marking/submission_summary.html', ctx)
