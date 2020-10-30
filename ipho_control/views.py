# from django.shortcuts import render

# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse

from django.forms import inlineformset_factory
from django.urls import reverse
from django.contrib.auth.decorators import (
    permission_required,
    user_passes_test,
)
from django.template.context_processors import csrf
from django.template.loader import render_to_string

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from ipho_control.models import ExamState, ExamHistory
from ipho_control.forms import ExamStateForm
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


def exam_state_context(is_superuser=False, exam_id=None):
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
            av_set = ExamState.get_available_exam_field_names()
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
    """Helper function to generate bootstrap alerts"""
    return f"""<div class="alert alert-{level} alert-dismissible" role="alert">
                <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <p>{msg}</p>
                </div>"""


@permission_required("ipho_core.is_staff")
def cockpit(request, exam_id=None, new_state=False):
    ctx = {}
    ctx["alerts"] = []
    ctx["h1"] = "Cockpit"
    exam_list, active_exam = exam_state_context(request.user.is_superuser, exam_id)
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
    if not request.user.is_superuser:
        states = states.filter(available_to_organizers=True)
    ctx["help_texts_settings"] = ExamState.get_exam_field_help_texts()
    ctx["checks_list"] = {}
    for state in states:
        ctx["checks_list"][state.pk] = state.run_checks(return_all=True)
    ctx["superuser"] = request.user.is_superuser
    ctx["states"] = states
    ctx["active_exam"] = active_exam
    ctx["exam_list"] = exam_list

    return render(request, "ipho_control/cockpit_base.html", context=ctx)


@permission_required("ipho_core.is_staff")
def switch_state(request, exam_id, state_id):
    """view to render the switch state modal"""
    exam = Exam.objects.filter(pk=exam_id).first()
    state = ExamState.objects.filter(pk=state_id).first()

    # check whether we can switch to this state
    if exam is None or state is None:
        return JsonResponse(
            {
                "success": False,
                "error": "Exam or State undefined. Please contact support.",
            }
        )
    if state.exam != exam:
        return JsonResponse(
            {
                "success": False,
                "error": "Exam and State do not match. Please contact support.",
            }
        )
    if not (
        state.is_applicable_organizers()
        or (state.is_applicable() and request.user.is_superuser)
    ):
        return JsonResponse({"success": False, "error": "Cannot switch to this state."})
    if request.method == "POST":
        state.apply(username=str(request.user))
        title = f"State <strong>{state.name}</strong> applied"
        body = ""
        return JsonResponse({"success": True, "title": title, "body": body})

    # run checks and refactor results
    checks = state.run_checks()
    warning_list = [w["message"] for w in checks["warnings"]]

    # get current exam settings
    available_setttings = ExamState.get_available_exam_field_names()
    current_exam_settings = {s: getattr(exam, s) for s in available_setttings}

    changelog = {"changed": [], "unchanged": []}
    for s in available_setttings:
        if current_exam_settings[s] == state.exam_settings[s]:
            changelog["unchanged"].append({"name": s, "new": state.exam_settings[s]})
        else:
            changed = {
                "name": s,
                "old": current_exam_settings[s],
                "new": state.exam_settings[s],
            }
            changelog["changed"].append(changed)
    ctx = {}
    ctx["state"] = state
    ctx["help_texts_settings"] = state.get_exam_field_help_texts()
    ctx["changelog"] = changelog
    ctx["warnings"] = warning_list
    ctx.update(csrf(request))
    body = render_to_string("ipho_control/switch_state.html", ctx)
    title = f"Switch Exam <strong>{exam.name}</strong> to State <strong>{state.name}</strong>"
    return JsonResponse({"success": True, "title": title, "body": body})


@permission_required("ipho_core.is_staff")
def exam_history(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    history = ExamHistory.objects.filter(exam=exam).order_by("-timestamp")
    ctx = {}
    ctx["help_texts_settings"] = ExamState.get_exam_field_help_texts()
    ctx["history"] = history
    res = {}
    res["body"] = render_to_string("ipho_control/exam_history.html", ctx)
    res["title"] = f"History for {exam.name}"
    res["success"] = True
    return JsonResponse(res)
