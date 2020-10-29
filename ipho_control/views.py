# from django.shortcuts import render

# Create your views here.

from django.shortcuts import get_object_or_404, render, redirect
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    HttpResponseNotModified,
    JsonResponse,
    Http404,
    HttpResponseForbidden,
)
from django.http.request import QueryDict

from django.urls import reverse
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.context_processors import csrf
from django.template import RequestContext
from django.template.loader import render_to_string
from django.db.models import (
    Q,
    Sum,
    Case,
    When,
    IntegerField,
    F,
    Max,
)

from ipho_control.models import ExamState
from ipho_control.forms import ExamStateForm


@user_passes_test(lambda u: u.is_superuser)
def add_state(request):
    ctx = {}
    ctx["alerts"] = []
    form = ExamStateForm(request.POST or None)
    print(form.is_valid())
    print(form.errors)
    if form.is_valid():
        form.save()

        ctx["alerts"].append(
            '<div class="alert alert-success"><p><strong>Success.</strong></p></div>'
        )
    ctx["form"] = form
    return render(request, "ipho_control/add_state.html", ctx)

@user_passes_test(lambda u: u.is_superuser)
def edit_state(request, state_id):
    state = get_object_or_404(ExamState, pk=state_id)
    ctx = {}
    ctx["alerts"] = []
    form = ExamStateForm(request.POST or None, instance=state)
    print(form.is_valid())
    print(form.errors)
    if form.is_valid():
        form.save()

        ctx["alerts"].append(
            '<div class="alert alert-success"><p><strong>Success.</strong></p></div>'
        )
    ctx["form"] = form
    return render(request, "ipho_control/add_state.html", ctx)
