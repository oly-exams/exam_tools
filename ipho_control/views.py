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

from django.forms import modelformset_factory, inlineformset_factory
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
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Submit,
    Layout,
    Field,
    Fieldset,
    MultiField,
    Div,
    HTML,
    Row,
)
from crispy_forms.bootstrap import InlineField

from ipho_control.models import ExamState
from ipho_control.forms import ExamStateForm, SwitchStateForm
from ipho_exam.models import Exam, Question


@user_passes_test(lambda u: u.is_superuser)
def add_edit_state(request, state_id=None):
    """view to add or edit ExamStates"""
    state = None
    ctx = {}
    ctx["alerts"] = []
    ctx["h1"] = "Add Exam State"
    ctx["lead"] = "Add another Exam State to the cockpit"
    if state_id is not None:
        state = get_object_or_404(ExamState, pk=state_id)
        ctx["h1"] = "Edit Exam State"
        ctx["lead"] = "Edit the following Exam State"
    form = ExamStateForm(request.POST or None, instance=state)
    if form.is_valid():
        form.save()

        ctx["alerts"].append(
            '<div class="alert alert-success"><p><strong>Success.</strong></p></div>'
        )
    ctx["form"] = form
    return render(request, "ipho_control/add_state.html", ctx)


def state_context(is_superuser=False, exam_id=None):
    """helper function to create context for cockpit_base.html"""
    exams = Exam.objects.order_by("name")
    if not is_superuser:
        exams = exams.filter(hidden=False)
    if exam_id is None:
        exam_id = exams.first().pk
    exams = exams.all()
    exam_list = []
    active_exam = None
    for exam in exams:
        ctx = {"exam": exam}
        state = ExamState.get_current_state(exam)
        if (
            not is_superuser
            and state is not None
            and not state.is_applicable_organizers()
        ):
            state = None
        if state is None:
            av_set = ExamState.get_available_exam_settings()
            exam_settings = {s: getattr(exam, s) for s in av_set}

            class UndefState:
                name = "Unnamed state"
                undef = True
                description = "This is not a predefined state. No additional information available."
                exam_settings = None
            undef_state = UndefState()
            undef_state.exam_settings = exam_settings

            ctx["undef_state"] = undef_state
        ctx["state"] = state
        ctx["active_tab"] = exam.pk == exam_id
        if ctx["active_tab"]:
            active_exam = ctx
        exam_list.append(ctx)

    return exam_list, active_exam

def alert_dismissible(msg, level="success"):
    return f"""<div class="alert alert-{level} alert-dismissible" role="alert">
                <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <p>{msg}</p>
                </div>"""

def cockpit(request, exam_id=None, new_state=False):
    ctx = {}
    ctx["alerts"] = []
    ctx["h1"] = "Cockpit"
    exam_list, active_exam = state_context(request.user.is_superuser, exam_id)
    exam = active_exam["exam"]
    state = active_exam["state"]
    if new_state:
        new_state_msg = f"<strong>Success.</strong> Changed state to {state.name}."
        ctx["alerts"].append(alert_dismissible(new_state_msg))
    if state is not None and state.get_available_question_settings():
        QuestionFormSet = inlineformset_factory(  # pylint: disable=invalid-name
            parent_model=Exam,
            model=Question,
            fields=state.get_available_question_settings(),
            extra=0,
            can_delete=False,
        )

        class QuestionFormSetHelper(FormHelper):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.form_method = "post"
                self.disable_csrf = False
                self.form_action = reverse(
                    "control:cockpit-id",
                    args=[
                        exam.pk,
                    ],
                )
                self.template = "ipho_control/table_inline_formset.html"
                self.render_required_fields = True
                self.add_input(Submit("submit", "Save"))

        formset = QuestionFormSet(request.POST or None, instance=exam)
        if formset.is_valid():
            formset.save()
            msg = "<strong>Success.</strong> Question settings saved."
            ctx["alerts"].append(alert_dismissible(msg))

        helper = QuestionFormSetHelper()
        ctx["question_settings"] = {"formset": formset, "helper": helper}
    if state is None and "undef_state" in active_exam:
        active_exam["state"] = active_exam["undef_state"]

    states = ExamState.objects.filter(exam=exam)

    ctx["states"] = states
    ctx["active_exam"] = active_exam
    ctx["exam_list"] = exam_list

    return render(request, "ipho_control/cockpit_base.html", context=ctx)


def switch_state(request, exam_id, state_id):
    """view to render the switch state modal"""
    exam = Exam.objects.filter(pk=exam_id).first()
    state = ExamState.objects.filter(pk=state_id).first()
    if exam is None or state is None:
        return JsonResponse({"success":False, "error": "Exam or State undefined. Please contact support."})
    if state.exam != exam:
        return JsonResponse({"success":False, "error": "Exam and State do not match. Please contact support."})
    if not (state.is_applicable_organizers() or (state.is_applicable() and request.user.is_superuser)):
        return JsonResponse({"success":False, "error": "Cannot switch to this state."})
    if request.method == "POST":
        state.apply()
        title = f"State <strong>{state.name}</strong> applied"
        body = ""
        return JsonResponse({'success':True,'title':title, 'body':body})
    # run checks and refactor results
    checks = state.run_checks()
    warning_list = [w['message'] for w in checks['warnings']]
    
    print(checks)
    print(warning_list)

    ctx = {"warnings":warning_list, }
    ctx["before_switch"] = state.before_switching
    ctx.update(csrf(request))
    body = render_to_string("ipho_control/switch_state.html", ctx)
    title = f"Switch Exam <strong>{exam.name}</strong> to State <strong>{state.name}</strong>"
    return JsonResponse({'success':True,'title':title, 'body':body})

def cockpit_base(request):
    """view to render the base of all cockpit views"""
    pass


def state_overview(request, exam_id):
    """view to display and edit all states"""
    pass


def exam_cockpit(request, exam_id):
    """view to display current state and question flags"""
    pass
