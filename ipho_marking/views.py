from django.shortcuts import get_object_or_404, render_to_response, render
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
    pass
