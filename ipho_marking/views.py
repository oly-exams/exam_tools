from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotModified, HttpResponseForbidden, JsonResponse, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.core.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string

from django.conf import settings
from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, VersionNode
from ipho_exam import qquery as qwquery
from ipho_exam import qml

from .models import MarkingMeta, Marking
from .forms import ImportForm

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
    return HttpResponse()

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
    exam = get_object_or_404(Exam, id=exam_id)
    return HttpResponse()
