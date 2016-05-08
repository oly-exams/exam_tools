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
from ipho_exam.models import Exam, Question, VersionNode, ExamAction
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
        for question in exam.question_set.filter(type='A'):
            qw = qwquery.latest_version(question_id=question.pk, lang_id=OFFICIAL_LANGUAGE)
            question_points,_,_ = qml.question_points(qw.qml)
            for i,(name, points) in enumerate(question_points):
                mmeta, created = MarkingMeta.objects.update_or_create(question=question, name=name,
                    defaults={'max_points': points, 'position': i})
                num_created += created
                num_tot += 1

                for student in Student.objects.all():
                    for version_id, version_name in Marking.MARKING_VERSIONS:
                        marking, created = Marking.objects.get_or_create(marking_meta=mmeta, student=student, version=version_id)
                        num_marking_created += created
                        num_marking_tot += 1

        ctx['alerts'].append('<div class="alert alert-success"><strong>Success.</strong> {} marking subquestion were imported.<ul><li> {} created</li><li>{} updated</li><li>{} student marking created</li><li>{} student marking already found</li>.</div>'.format(num_tot, num_created, num_tot-num_created, num_marking_created, num_marking_tot-num_marking_created))
    ctx['form'] = form
    return render(request, 'ipho_marking/import_exam.html', ctx)


@permission_required('ipho_core.is_staff')
def summary(request):
    pass

@permission_required('ipho_core.is_staff')
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

@login_required
def delegation_summary(request):
    delegation = Delegation.objects.get(members=request.user)
    points_submissions = ExamAction.objects.filter(delegation=delegation, action=ExamAction.POINTS, exam__active=True).order_by('exam')
    students = Student.objects.filter(delegation=delegation)
    ctx = {'students': students, 'points_submissions': points_submissions, 'OPEN_STATUS': ExamAction.OPEN, 'SUBMITTED_STATUS': ExamAction.SUBMITTED, }
    return render(request, 'ipho_marking/delegation_summary.html', ctx)

@login_required
def delegation_stud_detail(request, student_id, exam_id, question_id):
    delegation = Delegation.objects.get(members=request.user)
    student = get_object_or_404(Student, id=student_id)
    if student.delegation != delegation:
        return HttpResponseForbidden('You do not have permission to access this student.')

    question = get_object_or_404(Question, id=question_id)

    return HttpResponse()

@login_required
def delegation_confirm(request, exam_id):
    delegation = Delegation.objects.get(members=request.user)
    exam = get_object_or_404(Exam, id=exam_id, active=True)
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

    questions = Question.objects.filter(exam=exam, type='A')
    metas_query = MarkingMeta.objects.filter(question=questions)
    markings_query = Marking.objects.filter(student__delegation=delegation, marking_meta=metas_query, version='D').order_by('student','marking_meta__position')
    metas = {k: list(g) for k,g in itertools.groupby(metas_query, key=lambda m: m.question.pk)}
    markings = {k: list(g) for k,g in itertools.groupby(markings_query, key=lambda m: m.marking_meta.question.pk)}
    ctx = {'exam': exam, 'questions': questions, 'markings': markings, 'metas': metas, 'form_error': form_error}
    return render(request, 'ipho_marking/delegation_confirm.html', ctx)


@permission_required('ipho_core.is_staff')
def moderation_index(request, question_id=None):
    questions = Question.objects.filter(exam__hidden=False, type='A')
    question = None if question_id is None else get_object_or_404(Question, id=question_id)
    delegations = Delegation.objects.all()
    ctx={'questions': questions, 'question': question, 'delegations': delegations}
    return render(request, 'ipho_marking/moderation_index.html', ctx)

@permission_required('ipho_core.is_staff')
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

@permission_required('ipho_core.is_staff')
def moderation_confirmed(request, question_id, delegation_id):
    question = get_object_or_404(Question, id=question_id)
    delegation = get_object_or_404(Delegation, id=delegation_id)

    markings = Marking.objects.filter( marking_meta__question=question, version='F', student__delegation=delegation).values('student').annotate(total=Sum('points')).order_by('student').values('student__first_name', 'student__last_name', 'student__code', 'total')

    ctx = {'question': question, 'delegation': delegation, 'markings': markings}
    return render(request, 'ipho_marking/moderation_confirmed.html', ctx)
