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

from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse

from django.forms import inlineformset_factory
from django.urls import reverse
from django.contrib.auth.decorators import (
    permission_required,
    user_passes_test,
    login_required,
)
from django.template.context_processors import csrf
from django.template.loader import render_to_string

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from ipho_control.models import ExamPhase, ExamPhaseHistory
from ipho_control.forms import ExamPhaseForm
from ipho_exam.models import Exam, Question


@user_passes_test(lambda u: u.is_superuser)
def add_edit_phase(request, phase_id=None, exam_id=None):
    """View to add or edit ExamPhases."""
    phase = None
    ctx = {}
    ctx["alerts"] = []
    ctx["h1"] = "Add Exam Phase"
    ctx["lead"] = "Add another Exam Phase to the cockpit"
    if exam_id is not None:
        exam = get_object_or_404(Exam, pk=exam_id)
        phase = ExamPhase(exam=exam)
        ctx["h1"] = f"Add Exam Phase for { exam.name }"
    if phase_id is not None:
        phase = get_object_or_404(ExamPhase, pk=phase_id)
        ctx["h1"] = "Edit Exam Phase"
        ctx["lead"] = "Edit the following Exam Phase"

    form = ExamPhaseForm(request.POST or None, instance=phase)
    if form.is_valid():
        form.save()

        ctx["alerts"].append(
            '<div class="alert alert-success"><p><strong>Success.</strong></p></div>'
        )
    ctx["form"] = form
    return render(request, "ipho_control/add_phase.html", ctx)


def exam_phase_context(is_superuser=False, exam_id=None):
    """Helper function to create context for cockpit_base.html."""
    exams = Exam.objects.order_by("name")
    if not is_superuser:
        exams = exams.filter(hidden=False)
    if exam_id is None:
        if exams.exists():
            exam_id = exams.first().pk
        else:
            return [], None
    exams = exams.all()
    exam_list = []
    active_exam = None
    for exam in exams:
        ctx = {"exam": exam}
        phase = ExamPhase.get_current_phase(exam)
        if (
            not is_superuser
            and phase is not None
            and not phase.is_applicable_organizers()
        ):
            phase = None
        if phase is None:
            # Create a dummy phase
            av_set = ExamPhase.get_available_exam_field_names()
            exam_settings = {s: getattr(exam, s) for s in av_set}

            class UndefPhase:
                name = "Unnamed phase"
                undef = True
                description = "This is not a predefined phase. No additional information available."
                exam_settings = None

            undef_phase = UndefPhase()
            undef_phase.exam_settings = exam_settings

            ctx["undef_phase"] = undef_phase
        ctx["phase"] = phase
        ctx["active_tab"] = exam.pk == exam_id
        if ctx["active_tab"]:
            active_exam = ctx
        exam_list.append(ctx)

    return exam_list, active_exam


def alert_dismissible(msg, level="success"):
    """Helper function to generate bootstrap alerts."""
    return f"""<div class="alert alert-{level} alert-dismissible" role="alert">
                <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <p>{msg}</p>
                </div>"""


@permission_required("ipho_core.can_access_control")
def cockpit(request, exam_id=None, changed_phase=False, deleted_phase=False):
    """Main view for the control cockpit."""
    ctx = {}
    ctx["alerts"] = []
    ctx["h1"] = "Cockpit"
    exam_list, active_exam = exam_phase_context(request.user.is_superuser, exam_id)
    if active_exam is None:
        return render(
            request, "ipho_control/cockpit_base.html", context={"h1": "Cockpit"}
        )
    exam = active_exam["exam"]
    phase = active_exam["phase"]
    if changed_phase and phase is not None:
        changed_phase_msg = f"<strong>Success.</strong> Changed phase to {phase.name}."
        ctx["alerts"].append(alert_dismissible(changed_phase_msg))
    if deleted_phase:
        del_phase_msg = "<strong>Phase deleted.</strong>"
        ctx["alerts"].append(alert_dismissible(del_phase_msg, "warning"))

    if phase is not None and phase.get_available_question_settings():
        # create the formset for the question settings
        QuestionFormSet = inlineformset_factory(  # pylint: disable=invalid-name
            parent_model=Exam,
            model=Question,
            fields=phase.get_available_question_settings(),
            extra=0,
            can_delete=False,
        )
        # create the formset helper
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
                # use a custom template to render the question names
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
    if phase is None and "undef_phase" in active_exam:
        active_exam["phase"] = active_exam["undef_phase"]

    phases = ExamPhase.objects.filter(exam=exam)
    if not request.user.is_superuser:
        phases = phases.filter(available_to_organizers=True)
    ctx["help_texts_settings"] = ExamPhase.get_exam_field_help_texts()
    ctx["checks_list"] = {}
    for phase in phases:
        ctx["checks_list"][phase.pk] = phase.run_checks(return_all=True)
    ctx["superuser"] = request.user.is_superuser
    ctx["phases"] = phases
    ctx["active_exam"] = active_exam
    ctx["exam_list"] = exam_list

    return render(request, "ipho_control/cockpit_base.html", context=ctx)


@permission_required("ipho_core.can_access_control")
def switch_phase(request, exam_id, phase_id):
    """View for the switch phase modal."""
    exam = Exam.objects.filter(pk=exam_id).first()
    phase = ExamPhase.objects.filter(pk=phase_id).first()

    # check whether we can switch to this phase
    if exam is None or phase is None:
        return JsonResponse(
            {
                "success": False,
                "error": "Exam or Phase undefined. Please contact support.",
            }
        )
    if phase.exam != exam:
        return JsonResponse(
            {
                "success": False,
                "error": "Exam and Phase do not match. Please contact support.",
            }
        )
    if not (
        phase.is_applicable_organizers()
        or (phase.is_applicable() and request.user.is_superuser)
    ):
        return JsonResponse({"success": False, "error": "Cannot switch to this phase."})
    if request.method == "POST":
        phase.apply(username=str(request.user))
        title = f"Phase <strong>{phase.name}</strong> applied"
        body = ""
        return JsonResponse({"success": True, "title": title, "body": body})

    # run checks and refactor results
    checks = phase.run_checks()
    warning_list = [w["message"] for w in checks["warnings"]]

    # get current exam settings
    available_setttings = ExamPhase.get_available_exam_field_names()
    current_exam_settings = {s: getattr(exam, s) for s in available_setttings}

    # create changelog to display changes
    changelog = {"changed": {}, "unchanged": {}}
    for s in available_setttings:
        if current_exam_settings[s] == phase.exam_settings.get(s):
            changelog["unchanged"][s] = phase.exam_settings.get(s)
        else:
            changed = {
                "old": current_exam_settings.get(s),
                "new": phase.exam_settings.get(s),
            }
            changelog["changed"][s] = changed
    ctx = {}
    ctx["phase"] = phase
    ctx["help_texts_settings"] = phase.get_exam_field_help_texts()
    ctx["changelog"] = changelog
    ctx["warnings"] = warning_list
    ctx.update(csrf(request))
    body = render_to_string("ipho_control/switch_phase.html", ctx)
    title = f"Switch Exam <strong>{exam.name}</strong> to Phase <strong>{phase.name}</strong>"
    return JsonResponse({"success": True, "title": title, "body": body})


@user_passes_test(lambda u: u.is_superuser)
def delete_phase(request, phase_id):
    """View for the delete phase modal."""
    phase = get_object_or_404(ExamPhase, pk=phase_id)
    if request.method == "POST":
        phase.delete()
        return JsonResponse({"success": True})

    res = {}
    res["title"] = f"Delete phase {phase.name}"
    res["body"] = "Are you sure?"
    if phase.is_current_phase():
        res["body"] = "This is the <strong>current phase</strong>, are you really sure?"
    res["success"] = True
    return JsonResponse(res)


@permission_required("ipho_core.can_access_control")
def exam_history(request, exam_id):
    """View for the exam history modal."""
    exam = get_object_or_404(Exam, pk=exam_id)
    history = ExamPhaseHistory.objects.filter(exam=exam).order_by("-timestamp")
    ctx = {}
    ctx["help_texts_settings"] = ExamPhase.get_exam_field_help_texts()
    ctx["history"] = history
    res = {}
    res["body"] = render_to_string("ipho_control/exam_history.html", ctx)
    res["title"] = f"History for {exam.name}"
    res["success"] = True
    return JsonResponse(res)


@login_required
def exam_phase_summary(request):
    """View for the exam summary on home."""
    exams = Exam.objects.filter(hidden=False)
    if not request.user.has_perm("ipho_core.is_staff"):
        exams = exams.filter(active=True)
    if request.user.is_superuser:
        exams = Exam.objects

    phases = []
    for exm in exams.all():
        last_change = ExamPhaseHistory.get_latest(exam=exm)
        if last_change is not None:
            last_changed = last_change.timestamp
        else:
            last_changed = None
        phases.append(
            {
                "exam": exm,
                "phase": ExamPhase.get_current_phase(exm),
                "last_change": last_changed,
            }
        )
    ctx = {}
    ctx["phases"] = phases
    body = render_to_string("ipho_control/phase_summary.html", ctx)
    res = {"success": True, "body": body}
    return JsonResponse(res)
