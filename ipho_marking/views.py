# pylint: disable=too-many-lines, consider-using-f-string
import csv
import decimal
import itertools
from collections import OrderedDict, namedtuple
from hashlib import md5

import pandas as pd
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.db.models import Count, F, Q, Sum
from django.forms import modelformset_factory
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ipho_core.models import Delegation, Student
from ipho_exam.models import Document, Exam, Participant, Question

from .export_marking import get_version_marks
from .forms import ImportForm, PointsForm, UploadMarkingForm
from .import_marking import generate_template, import_marking
from .models import (
    Marking,
    MarkingAction,
    MarkingMeta,
    QuestionPointsRescale,
    generate_markings_from_exam,
    sum_if_not_none,
)

OFFICIAL_LANGUAGE_PK = 1
OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")
ALLOW_MARKS_NONE = getattr(settings, "ALLOW_MARKS_NONE", False)
SHOW_PARTICIPANT_NAME_TO_MARKERS = getattr(
    settings, "SHOW_PARTICIPANT_NAME_TO_MARKERS", True
)

DiffColorPair = namedtuple("DiffColorPair", ["O", "D"])
EmptyMarking = namedtuple("EmptyMarking", ["points", "comment"])


def get_diff_color_pair(official, delegation):
    if official == delegation:
        return DiffColorPair("", "")
    if delegation is None or official is not None and official > delegation:
        return DiffColorPair("info", "warning")
    return DiffColorPair("warning", "info")


def get_valid_marking_question_list(request, exam, editable):
    question_list = []

    answer_sheet_list = Question.objects.filter(exam=exam, type=Question.ANSWER)

    for answer_sheet in answer_sheet_list:
        if not editable:
            question_list.append(answer_sheet)
        else:
            delegation = Delegation.objects.filter(members=request.user).first()
            action = MarkingAction.objects.get(
                delegation=delegation, question=answer_sheet
            )
            if (
                action.status < MarkingAction.SUBMITTED_FOR_MODERATION
                and answer_sheet.exam.marking_delegation_action
                >= Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT
            ):
                question_list.append(answer_sheet)

    return question_list


def get_points_per_student(exams, students, markings):
    """Obtains points per student for each exam."""
    points_per_student = []
    for student in students:
        # Exam points
        ppnt_exam_points_list = []
        for exam in exams:
            participant = student.participant_set.filter(exam=exam).first()
            # if there are no open/submitted marking actions:
            if not MarkingAction.objects.filter(
                question__exam=exam,
                delegation=student.delegation,
                # status__lte=MarkingAction.SUBMITTED_FOR_MODERATION,
            ).exists():
                points_exam = QuestionPointsRescale.external_sum_for_exam(
                    markings, participant.code, exam
                )
                ppnt_exam_points_list.append(points_exam)
            else:
                ppnt_exam_points_list.append(None)

        not_none_pts = [p for p in ppnt_exam_points_list if p is not None]
        # As sum([]) = 0 would give a total =0 for None points, we need to set it to None by hand
        if not_none_pts and not_none_pts == ppnt_exam_points_list:
            total = sum(p for p in ppnt_exam_points_list if p is not None)
        else:
            total = None
        points_per_student.append((student, ppnt_exam_points_list, total))
    return points_per_student


@permission_required("ipho_core.is_organizer_admin")
def import_exam(request):
    ctx = {}
    ctx["alerts"] = []
    form = ImportForm(request.POST or None)
    if form.is_valid():
        exam = form.cleaned_data["exam"]
        (
            num_tot,
            num_created,
            num_marking_tot,
            num_marking_created,
        ) = generate_markings_from_exam(exam, user=request.user)

        ctx["alerts"].append(
            '<div class="alert alert-success"><p><strong>Success.</strong></p><p>{} marking subquestion were imported.<p><ul><li>{} created</li><li>{} updated</li></ul><p>{} participant marking created.</p><ul><li>{} participant marking already found</li></ul></div>'.format(
                num_tot,
                num_created,
                num_tot - num_created,
                num_marking_created,
                num_marking_tot - num_marking_created,
            )
        )
    ctx["form"] = form
    return render(request, "ipho_marking/import_exam.html", ctx)


@permission_required("ipho_core.is_marker")
def summary(request):  # pylint: disable=too-many-locals
    vid = request.GET.get("version", "O")
    markings = Marking.objects.for_user(request.user, version=vid)
    editable_markings = Marking.objects.editable(request.user, version=vid)

    questions = (
        Question.objects.for_user(request.user)
        .filter(markingmeta__isnull=False)
        .order_by("exam", "position")
        .values(
            "pk",
            "exam__name",
            "name",
        )
        .annotate(max_int_points=Sum("markingmeta__max_points"))
        .annotate(min_int_points=Sum("markingmeta__min_points"))
        .values("max_int_points", "min_int_points", "pk", "exam__name", "name")
        .distinct()
    )

    for quest in questions:
        qscale = QuestionPointsRescale.objects.filter(question__id=quest["pk"]).first()

        if quest["min_int_points"] is None or quest["max_int_points"] is None:
            quest["points_transformed"] = False
            continue
        if not qscale:
            quest["points_transformed"] = False
            continue
        if qscale.numerator / qscale.denominator == 1 and qscale.shift == 0:
            quest["points_transformed"] = False
            continue
        quest["points_transformed"] = True

        quest["max_ext_points"] = qscale.transform(quest["max_int_points"])
        quest["min_ext_points"] = qscale.transform(quest["min_int_points"])

    exams = []
    for exam in (
        Exam.objects.for_user(request.user)
        .filter(question__markingmeta__isnull=False)
        .distinct()
    ):
        min_p, max_p = QuestionPointsRescale.min_max_points_for_exam(exam)
        exams.append(
            {"pk": exam.pk, "name": exam.name, "min_total": min_p, "max_total": max_p}
        )

    points_per_participant = []
    participants = [
        (c, list(ps))
        for c, ps in itertools.groupby(
            Participant.objects.all().values("id", "code", "exam__name"),
            key=lambda p: p["code"],
        )
    ]
    for code, participant_group in participants:
        ppnt_question_points_list = []
        ppnt_question_editable_list = []
        ppnt_question_id_list = []
        for question in questions:
            ppnt_markings_question = markings.filter(
                marking_meta__question=question["pk"],
                participant__code=code,
            )
            if ppnt_markings_question.filter(points__isnull=True).exists():
                points_question = "-"
            else:
                points_question = ppnt_markings_question.aggregate(Sum("points"))[
                    "points__sum"
                ]
            ppnt_question_points_list.append(points_question)

            editable = editable_markings.filter(
                marking_meta__question=question["pk"],
                participant__code=code,
            ).exists()
            if editable:
                ppnt_question_editable_list.append(question["pk"])
            else:
                ppnt_question_editable_list.append(False)
            # pylint: disable=invalid-name
            ps = [
                p
                for p in participant_group
                if p["exam__name"] == question["exam__name"]
            ]
            ppnt_question_id_list.append(ps[0]["id"] if ps else None)

        ppnt_exam_points_list = []
        for exam in exams:
            points_exam = QuestionPointsRescale.external_sum_for_exam(
                markings, participant_code=code, exam=exam["pk"]
            )
            ppnt_exam_points_list.append(points_exam)

        points_per_participant.append(
            (
                code,
                list(
                    zip(
                        ppnt_question_points_list,
                        ppnt_question_editable_list,
                        ppnt_question_id_list,
                    )
                ),
                ppnt_exam_points_list,
            )
        )

    context = {
        "vid": vid,
        "version": Marking.MARKING_VERSIONS[vid],
        "all_versions": Marking.MARKING_VERSIONS,
        "questions": questions,
        "points_per_participant": points_per_participant,
        "exams": exams,
    }
    return render(request, "ipho_marking/summary.html", context)


@permission_required("ipho_core.is_marker")
def staff_ppnt_detail(request, version, ppnt_id, question_id):
    ctx = {}
    ctx["msg"] = []

    if not request.user.has_perm("ipho_core.is_marker") or version != "O":
        raise Http404(
            "You cannot modify these markings since you are not a marker or you are trying to edit a delegation or final marking"
        )

    question = get_object_or_404(
        Question.objects.for_user(request.user), id=question_id
    )
    participant = get_object_or_404(Participant, id=ppnt_id)

    marking_action = get_object_or_404(
        MarkingAction, delegation=participant.delegation, question=question
    )
    if marking_action.status == MarkingAction.FINAL:
        raise Http404("These markings are final, you cannot modify them!")

    metas = MarkingMeta.objects.filter(question=question)
    marking_query = Marking.objects.editable(request.user, version=version).filter(
        marking_meta__in=metas, participant=participant
    )
    if not marking_query.exists():
        raise Http404("You cannot modify these markings!")

    FormSet = modelformset_factory(  # pylint: disable=invalid-name
        Marking,
        form=PointsForm,
        fields=["points", "comment"],
        extra=0,
        can_delete=False,
        can_order=False,
    )
    form = FormSet(request.POST or None, queryset=marking_query)
    if form.is_valid():
        form.save()
        ctx["msg"].append(
            (
                "alert-success",
                '<strong>Succses.</strong> Points have been saved. <a href="{}#details" class="btn btn-default btn-xs">back to summary</a>'.format(
                    reverse("marking:summary")
                ),
            )
        )

    ctx["version"] = version
    ctx["version_display"] = Marking.MARKING_VERSIONS[version]
    ctx["participant"] = participant
    ctx["question"] = question
    ctx["exam"] = question.exam
    ctx["form"] = form
    return render(request, "ipho_marking/staff_edit.html", ctx)


@permission_required("ipho_core.is_organizer_admin")
def export_sql(request, versions):
    response = HttpResponse(content_type="text/csv")
    version_string = "_".join(versions)
    response[
        "Content-Disposition"
    ] = f'attachment; filename="markings_{version_string}.csv"'

    df = get_version_marks(versions)
    df.to_csv(response)
    return response


@permission_required("ipho_core.is_organizer_admin")
def export(
    request, include_totals=False
):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    versions = request.GET.get("v", "O,D,F").split(",")

    csv_rows = []
    title_row = ["Student", "First_Name", "Last_Name", "Delegation", "Version"]
    mmeta = MarkingMeta.objects.for_user(request.user).all()
    for meta in mmeta:
        title_row.append(f"{meta.question.name} - {meta.name} ({meta.max_points})")
    exams = Exam.objects.for_user(request.user)
    questions = Question.objects.for_user(request.user).filter(type=Question.ANSWER)
    if include_totals:
        for question in questions:

            title_row.append(f"Question Total: {question.exam.name} - {question.name}")
        for exam in exams:
            title_row.append(f"Exam Total: {exam.name}")
        title_row.append("Student Total")

    csv_rows.append(title_row)

    # pylint: disable=too-many-nested-blocks
    for student in Student.objects.all():
        participants = student.participant_set.all()
        for version in versions:
            ppnt_markings = Marking.objects.filter(
                participant__in=participants, marking_meta__in=mmeta, version=version
            )

            # visible_ppnt_markings = Marking.objects.for_user(
            #    request.user, version
            # ).filter(participants__in=participant, marking_meta__in=mmeta)
            row = [
                student.code,
                student.first_name,
                student.last_name,
                student.delegation.name,
                version,
            ]

            # directly iterating over is much simpler but a bit slower than using querysets
            points = []
            all_visible = True
            for marking in ppnt_markings:
                delegation = student.delegation
                action = MarkingAction.objects.get(
                    delegation=delegation, question=marking.marking_meta.question
                )
                if version == "O":
                    points.append(marking.points)
                elif (
                    version == "D"
                    and marking.marking_meta.question.exam.marking_organizer_can_see_delegation_marks
                    >= Exam.MARKING_ORGANIZER_VIEW_MODERATION_FINAL
                    and action.status >= MarkingAction.SUBMITTED_FOR_MODERATION
                    and (
                        action.status >= MarkingAction.LOCKED_BY_MODERATION
                        or marking.marking_meta.question.exam.marking_organizer_can_see_delegation_marks
                        >= Exam.MARKING_ORGANIZER_VIEW_WHEN_SUBMITTED
                    )
                ):
                    points.append(marking.points)
                elif version == "F" and action.status >= MarkingAction.FINAL:
                    points.append(marking.points)
                else:
                    all_visible = False
                    points.append(None)

            row += points
            if include_totals:
                for question in questions:
                    # Only append total if all markings are visible
                    q_markings = ppnt_markings.filter(marking_meta__question=question)
                    # If some marks are not visible
                    if (
                        all_visible
                    ):  # q_markings.exclude(pk__in=visible_ppnt_markings).exists():
                        row.append(_get_total(q_markings))
                    else:
                        row.append(None)

                student_total = 0
                no_none = False
                for exam in exams:
                    # Only append total if all markings are visible
                    # If some marks are not visible
                    if (
                        all_visible
                    ):  # e_markings.exclude(pk__in=visible_ppnt_markings).exists():
                        e_markings = ppnt_markings.filter(
                            marking_meta__question__exam=exam
                        )
                        points_exam = QuestionPointsRescale.external_sum_for_exam(
                            e_markings, participant_code=None, exam=None
                        )
                        if points_exam is not None:
                            student_total += points_exam
                        else:
                            no_none = False
                        row.append(points_exam)
                    else:
                        row.append(None)

                # Only append total if all markings are visible and none are None
                if all_visible and no_none:
                    pass
                else:
                    student_total = None
                row.append(student_total)
            row = ["-" if v is None else v for v in row]
            csv_rows.append(row)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="markings.csv"'

    writer = csv.writer(response)
    writer.writerows(csv_rows)

    return response


def _get_total(filtered_markings):
    return filtered_markings.aggregate(total=Sum(F("points")))["total"]


@permission_required("ipho_core.is_delegation")
def delegation_export(
    request, exam_id=None
):  # pylint: disable=too-many-branches, too-many-locals
    delegation = Delegation.objects.get(members=request.user)
    if exam_id is not None:
        exams = Exam.objects.for_user(request.user).filter(pk=exam_id)
    else:
        exams = Exam.objects.for_user(request.user)

    versions = request.GET.get("v", "O,D,F").split(",")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="markings.csv"'

    writer = csv.writer(response)
    participants = [
        (code, list(p))
        for code, p in itertools.groupby(
            Participant.objects.filter(delegation=delegation, exam__in=exams),
            key=lambda p: p.code,
        )
    ]

    row1 = ["Participant"]
    row2 = ["Version"]
    for code, __ in participants:
        for version in versions:
            row1.append(code)
            row2.append(Marking.MARKING_VERSIONS[version])
    writer.writerow(row1)
    writer.writerow(row2)
    totals = [decimal.Decimal(0)] * (len(row1) - 1)

    mmeta = MarkingMeta.objects.for_user(request.user).filter(question__exam__in=exams)
    for meta in mmeta:
        marking_action = MarkingAction.objects.get(
            delegation=delegation, question=meta.question
        )
        row = [f"{meta.question.name} - {meta.name} ({meta.max_points})"]
        i = 0
        for code, __ in participants:
            for version in versions:
                marking = Marking.objects.filter(
                    participant__code=code, version=version, marking_meta=meta
                )
                if marking.exists():
                    marking = marking.first()
                    if version == "D":
                        pass
                    elif (
                        version == "F"
                        and marking_action.status >= MarkingAction.LOCKED_BY_MODERATION
                    ):
                        pass
                    elif (
                        version == "O"
                        and meta.question.exam.marking_delegation_can_see_organizer_marks
                        >= Exam.MARKING_DELEGATION_VIEW_WHEN_SUBMITTED
                        and (
                            marking_action.status
                            >= MarkingAction.SUBMITTED_FOR_MODERATION
                            or meta.question.exam.marking_delegation_can_see_organizer_marks
                            >= Exam.MARKING_DELEGATION_VIEW_YES
                        )
                    ):
                        pass
                    else:
                        marking = None
                else:
                    marking = None
                if marking is not None:
                    points = marking.points
                else:
                    points = None
                row.append(points)
                if points is not None:
                    totals[i] += points
                i += 1
        row = ["-" if v is None else v for v in row]
        writer.writerow(row)

    row = ["Total"]
    writer.writerow(row + totals)

    return response


@permission_required("ipho_core.is_delegation")
def delegation_summary(
    request,
):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements

    delegation = Delegation.objects.get(members=request.user)
    students = Student.objects.filter(delegation=delegation)

    exam_marking_list = []
    exam_filter = Q(
        marking_delegation_action__gte=Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT
    ) | Q(
        marking_delegation_can_see_organizer_marks__gte=Exam.MARKING_DELEGATION_VIEW_WHEN_SUBMITTED
    )
    exams = Exam.objects.for_user(request.user).filter(exam_filter)

    for exam in exams:
        participants = Participant.objects.filter(delegation=delegation, exam=exam)
        answer_sheet_list = Question.objects.filter(exam=exam, type=Question.ANSWER)

        participant_list = []
        view_all = {a.pk: True for a in answer_sheet_list}
        edit_all = {a.pk: True for a in answer_sheet_list}

        # create the links for each participant
        for participant in participants:
            participant_ctx = {
                "pk": participant.pk,
                "code": participant.code,
                "full_name": participant.full_name,
            }
            question_list = []
            for question in answer_sheet_list:
                question_ctx = {"pk": question.pk}

                delegation = Delegation.objects.filter(members=request.user).first()
                action = MarkingAction.objects.get(
                    delegation=delegation, question=question
                )
                if (
                    action.status < MarkingAction.SUBMITTED_FOR_MODERATION
                    and question.exam.marking_delegation_action
                    >= Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT
                ):
                    editable_markings = Marking.objects.filter(
                        version="D",
                        participant__delegation=delegation,
                        marking_meta__question=question,
                    )
                else:
                    editable_markings = Marking.objects.none()

                # viewable markings always exsit (when there are questions to view)
                question_ctx["view"] = True
                question_ctx["edit"] = editable_markings.exists()

                # TODO: place in view marks view (view should always be enabled)
                if not question_ctx["view"]:
                    view_all[question.pk] = False
                    if (
                        exam.marking_delegation_can_see_organizer_marks
                        == Exam.MARKING_DELEGATION_VIEW_WHEN_SUBMITTED
                    ):
                        question_ctx[
                            "view_tooltip"
                        ] = f"Official marks are shown once you submitted your marks for {_('moderation')}."
                    else:
                        question_ctx[
                            "view_tooltip"
                        ] = "Official marks are not yet ready."
                if not question_ctx["edit"]:
                    edit_all[question.pk] = False
                    if exam.delegation_can_submit_marking():
                        question_ctx[
                            "edit_tooltip"
                        ] = "Marks already submitted. You cannot edit them anymore."
                    else:
                        question_ctx["edit_tooltip"] = "Marking is not yet activated"
                question_list.append(question_ctx)

            participant_ctx["questions"] = question_list
            participant_list.append(participant_ctx)

        question_list = []

        for question in answer_sheet_list:
            question_ctx = {
                "name": question.name,
                "pk": question.pk,
                "position": question.position,
                "view_all": view_all[question.pk],
                "edit_all": edit_all[question.pk],
            }
            marking_status = get_object_or_404(
                MarkingAction, delegation=delegation, question=question
            ).status

            action_button = None

            if marking_status == MarkingAction.OPEN:
                action_button = {
                    "link": reverse("marking:delegation-confirm", args=(question.pk,)),
                    "text": "Submit marks to organizers",
                }
            elif marking_status == MarkingAction.SUBMITTED_FOR_MODERATION:
                if (
                    settings.ACCEPT_MARKS_BEFORE_MODERATION
                    and question.exam.delegation_can_finalize_marking()
                ):
                    action_button = {
                        "link": reverse(
                            "marking:delegation-final-confirm", args=(question.pk,)
                        ),
                        "text": f"Sign off official marks without {_('moderation')}",
                        "tooltip": f"You don't need to do anything if you want to have a {_('moderation')}.",
                    }
            elif marking_status == MarkingAction.LOCKED_BY_MODERATION:
                if (
                    settings.SIGN_OFF_FINAL_MARKS
                    and question.exam.delegation_can_finalize_marking()
                ):
                    action_button = {
                        "link": reverse(
                            "marking:delegation-final-confirm", args=(question.pk,)
                        ),
                        "text": f"Sign off final marks from {_('moderation')}",
                        "class": "btn-success",
                        "tooltip": f"You can either accept the final marks or reopen the {_('moderation')} again.",
                    }
            elif marking_status == MarkingAction.FINAL:
                action_button = {
                    "nolink": True,
                    "text": "Final marks signed off",
                    "class": "btn-success",
                    "disabled": True,
                }
            actions = [
                action_button,
            ]
            question_ctx["actions"] = actions
            question_list.append(question_ctx)

        exam_ctxt = {
            "participants": participant_list,
            "questions": question_list,
            "name": exam.name,
            "pk": exam.pk,
            "code": exam.code,
        }
        exam_marking_list.append(exam_ctxt)

    # Final points pane
    vid = "F"
    markings = Marking.objects.for_user(request.user, vid)
    points_per_student = get_points_per_student(exams, students, markings)

    # We need a list of exams and total number of points for the header of the table
    exams_with_totals = [
        {
            "question__exam__name": exam.name,
            "exam_points": QuestionPointsRescale.min_max_points_for_exam(exam)[1],
        }
        for exam in exams
    ]

    # scans pane
    scans_table_per_exam = []
    scan_show_exams = Exam.objects.for_user(request.user).filter(
        delegation_scan_access__gte=Exam.DELEGATION_SCAN_ACCESS_STUDENT_ANSWER
    )
    for exam in scan_show_exams:
        participants = Participant.objects.filter(delegation=delegation, exam=exam)
        questions = exam.question_set.filter(type=Question.ANSWER)
        scans_of_participants = []
        for participant in participants.filter(exam=exam):
            # Scans
            # Scans with status other than 'S' are skipped in the HTML
            # template. That is easier, because it allows correctly
            # continuing the table.
            ppnt_exam_scans_list = (
                Document.objects.for_user(request.user)
                .filter(participant=participant)
                .exclude(position=0)  # remove general instructions
            )

            scans_of_participants.append((participant, ppnt_exam_scans_list))

        scans_table_per_exam.append((exam, questions, scans_of_participants))

    ctx = {
        "delegation": delegation,
        "exam_list": exam_marking_list,
        "final_points_exams": exams_with_totals,
        "points_per_student": points_per_student,
        "scans_table_per_exam": scans_table_per_exam,
    }
    return render(request, "ipho_marking/delegation_summary.html", ctx)


@permission_required("ipho_core.is_delegation")
def delegation_ppnt_edit(
    request, ppnt_id, question_id
):  # pylint: disable=too-many-locals
    delegation = Delegation.objects.get(members=request.user)

    question = get_object_or_404(
        Question.objects.for_user(request.user),
        id=question_id,
    )
    participant = get_object_or_404(Participant, id=ppnt_id, exam=question.exam)
    if participant.delegation != delegation:
        return HttpResponseForbidden(
            "You do not have permission to access this participant."
        )

    ctx = {}
    ctx["msg"] = []
    ctx["participant"] = participant
    ctx["participant_list"] = delegation.get_participants(question.exam)
    ctx["question"] = question
    ctx["question_list"] = get_valid_marking_question_list(
        request, question.exam, editable=True
    )
    ctx["exam"] = question.exam

    marking_action, __ = MarkingAction.objects.get_or_create(
        question=question, delegation=delegation
    )
    if not marking_action.in_progress():
        raise Http404(
            mark_safe(
                "<strong>Note:</strong> The points have been submitted, you can no longer edit them."
            )
        )

    metas = MarkingMeta.objects.filter(question=question)

    delegation = Delegation.objects.filter(members=request.user).first()
    if (
        marking_action.status < MarkingAction.SUBMITTED_FOR_MODERATION
        and question.exam.marking_delegation_action
        >= Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT
    ):
        marking_query = Marking.objects.filter(
            version="D", participant=participant, marking_meta__question=question
        )
    else:
        marking_query = Marking.objects.none()

    if not marking_query.exists():
        raise Http404("You cannot modify these markings!")

    FormSet = modelformset_factory(  # pylint: disable=invalid-name
        Marking,
        form=PointsForm,
        fields=["points", "comment"],
        extra=0,
        can_delete=False,
        can_order=False,
    )
    form = FormSet(
        request.POST or None,
        queryset=marking_query,
    )
    if (
        question.exam.marking_delegation_can_see_organizer_marks
        >= Exam.MARKING_DELEGATION_VIEW_YES
    ):
        official_marking = {
            x.marking_meta_id: x
            for x in Marking.objects.filter(
                marking_meta__in=metas, participant=participant, version="O"
            )
        }
        for form_item in form:
            points = official_marking[form_item.instance.marking_meta_id]
            form_item.official = points
        ctx["show_official_marks"] = True

    # if the editable set changes between GETting and POSTing the form,
    # is_valid() will raise a RelatedObjectDoesNotExist error
    try:
        is_valid = form.is_valid()
    except MarkingMeta.DoesNotExist as err:
        raise Http404("Cannot modify those markings.") from err
    if is_valid:
        form.save()
        participants = delegation.get_participants(question.exam)
        ppnt_id_list = [str(s.id) for s in participants]
        next_ppnt_index = ppnt_id_list.index(str(ppnt_id)) + 1
        next_ppnt_button = ""
        if next_ppnt_index < len(ppnt_id_list):
            next_ppnt_id = ppnt_id_list[next_ppnt_index]
            next_ppnt_button = ' <a href="{}" class="btn btn-default btn-xs">next participant</a> '.format(
                reverse(
                    "marking:delegation-ppnt-detail-edit",
                    kwargs={"ppnt_id": next_ppnt_id, "question_id": question_id},
                )
            )

        ctx["msg"].append(
            (
                "alert-success",
                "<strong>Success.</strong> Points have been saved."
                + next_ppnt_button
                + ' <a href="{}#details" class="btn btn-default btn-xs">back to summary</a> '.format(
                    reverse("marking:delegation-summary")
                ),
            )
        )

    documents = Document.objects.for_user(request.user).filter(
        participant=participant, position=question.position
    )

    ctx["form"] = form
    ctx["documents"] = documents
    return render(request, "ipho_marking/delegation_detail.html", ctx)


@permission_required("ipho_core.is_delegation")
def delegation_edit_all(request, question_id):
    delegation = Delegation.objects.get(members=request.user)

    question = get_object_or_404(
        Question.objects.for_user(request.user),
        id=question_id,
    )
    participants = Participant.objects.filter(delegation=delegation, exam=question.exam)

    ctx = {}
    ctx["msg"] = []
    ctx["participants"] = participants
    ctx["question"] = question
    ctx["exam"] = question.exam

    marking_action, __ = MarkingAction.objects.get_or_create(
        question=question, delegation=delegation
    )
    if not marking_action.in_progress():
        raise Http404(
            mark_safe(
                "<strong>Note:</strong> The points have been submitted, you can no longer edit them."
            )
        )

    delegation = Delegation.objects.filter(members=request.user).first()
    if (
        marking_action.status < MarkingAction.SUBMITTED_FOR_MODERATION
        and question.exam.marking_delegation_action
        >= Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT
    ):
        marking_query = Marking.objects.filter(
            version="D", participant__in=participants, marking_meta__question=question
        )
    else:
        marking_query = Marking.objects.none()

    if not marking_query.exists():
        raise Http404("You cannot modify these markings!")

    if (
        question.exam.marking_delegation_can_see_organizer_marks
        >= Exam.MARKING_DELEGATION_VIEW_YES
    ):
        ctx["show_official_marks"] = True

    FormSet = modelformset_factory(  # pylint: disable=invalid-name
        Marking,
        form=PointsForm,
        fields=["points", "comment"],
        extra=0,
        can_delete=False,
        can_order=False,
    )
    formset = FormSet(request.POST or None, queryset=marking_query)

    # if the editable set changes between GETting and POSTing the form,
    # is_valid() will raise a RelatedObjectDoesNotExist error
    try:
        is_valid = formset.is_valid()
    except MarkingMeta.DoesNotExist as err:
        raise Http404("Cannot modify those markings.") from err
    if is_valid:
        formset.save()
        ctx["msg"].append(
            (
                "alert-success",
                '<strong>Success.</strong> Points have been saved. <a href="{}#details" class="btn btn-default btn-xs">back to summary</a>'.format(
                    reverse("marking:delegation-summary")
                ),
            )
        )
    if formset.total_error_count() > 0:
        ctx["msg"].append(
            (
                "alert-danger",
                "<strong>Error.</strong> The submission could not be completed. See below for the errors.",
            )
        )

    documents = Document.objects.for_user(request.user).filter(
        position=question.position, participant__in=participants
    )

    ctx["documents"] = documents
    ctx["formset"] = formset
    return render(request, "ipho_marking/delegation_detail_all.html", ctx)


@permission_required("ipho_core.is_delegation")
def delegation_ppnt_view(request, ppnt_id, question_id):
    delegation = Delegation.objects.get(members=request.user)

    question = get_object_or_404(
        Question.objects.for_user(request.user), id=question_id
    )
    participant = get_object_or_404(Participant, id=ppnt_id, exam=question.exam)
    if participant.delegation != delegation:
        return HttpResponseForbidden(
            "You do not have permission to access this participant."
        )
    versions = ["O", "D", "F"]
    versions_display = [Marking.MARKING_VERSIONS[v] for v in versions]

    ctx = {}
    ctx["msg"] = []
    ctx["participant"] = participant
    ctx["participant_list"] = delegation.get_participants(question.exam)
    ctx["question"] = question
    ctx["question_list"] = get_valid_marking_question_list(
        request, question.exam, editable=False
    )
    ctx["exam"] = question.exam
    ctx["versions_display"] = versions_display

    marking_action, __ = MarkingAction.objects.get_or_create(
        question=question, delegation=delegation
    )

    if (
        marking_action.in_progress()
        and question.exam.marking_delegation_can_see_organizer_marks
        == Exam.MARKING_DELEGATION_VIEW_WHEN_SUBMITTED
    ):
        ctx["msg"].append(
            (
                ("alert-info"),
                "<strong>Note:</strong> You can see the official points only when you confirmed your markings.",
            )
        )

    if (
        question.exam.marking_delegation_can_see_organizer_marks
        == Exam.MARKING_DELEGATION_VIEW_NO
    ):
        ctx["msg"].append(
            (
                ("alert-info"),
                "<strong>Note:</strong> The official marks are not yet visible.",
            )
        )

    metas = MarkingMeta.objects.filter(question=question).all()

    grouped_markings = []
    for meta in metas:
        version_dict = {}
        for version in versions:

            marking = Marking.objects.get(
                participant=participant, version=version, marking_meta=meta
            )

            if version == "D":
                pass
            elif (
                version == "F"
                and marking_action.status >= MarkingAction.LOCKED_BY_MODERATION
            ):
                pass
            elif (
                version == "O"
                and question.exam.marking_delegation_can_see_organizer_marks
                >= Exam.MARKING_DELEGATION_VIEW_WHEN_SUBMITTED
                and (
                    marking_action.status >= MarkingAction.SUBMITTED_FOR_MODERATION
                    or question.exam.marking_delegation_can_see_organizer_marks
                    >= Exam.MARKING_DELEGATION_VIEW_YES
                )
            ):
                pass
            else:
                marking = None

            if marking is not None:
                pass
            else:
                marking = EmptyMarking(None, "")
            version_dict[version] = marking

        empty = EmptyMarking(None, "")
        version_dict["diff_color"] = get_diff_color_pair(
            version_dict.get("O", empty).points, version_dict.get("D", empty).points
        )
        grouped_markings.append((meta, version_dict))

    documents = Document.objects.for_user(request.user).filter(
        participant=participant, position=question.position
    )

    ctx["documents"] = documents
    ctx["markings"] = grouped_markings
    return render(request, "ipho_marking/delegation_detail.html", ctx)


@permission_required("ipho_core.is_delegation")
def delegation_view_all(request, question_id):
    delegation = Delegation.objects.get(members=request.user)
    question = get_object_or_404(
        Question.objects.for_user(request.user),
        id=question_id,
    )
    participants = Participant.objects.filter(delegation=delegation, exam=question.exam)
    versions = ["O", "D", "F"]
    versions_display = [Marking.MARKING_VERSIONS[v] for v in versions]

    ctx = {}
    ctx["msg"] = []
    ctx["question"] = question
    ctx["participants"] = participants
    ctx["exam"] = question.exam
    ctx["versions_display"] = versions_display

    marking_action, __ = MarkingAction.objects.get_or_create(
        question=question, delegation=delegation
    )

    if (
        marking_action.in_progress()
        and question.exam.marking_delegation_can_see_organizer_marks
        == Exam.MARKING_DELEGATION_VIEW_WHEN_SUBMITTED
    ):
        ctx["msg"].append(
            (
                ("alert-info"),
                "<strong>Note:</strong> You can see the official points only when you confirmed your markings.",
            )
        )

    if (
        question.exam.marking_delegation_can_see_organizer_marks
        == Exam.MARKING_DELEGATION_VIEW_NO
    ):
        ctx["msg"].append(
            (
                ("alert-info"),
                "<strong>Note:</strong> The official marks are not yet visible.",
            )
        )

    metas = MarkingMeta.objects.filter(question=question)

    grouped_markings = []
    for meta in metas:
        participant_list = []
        for participant in participants:
            version_dict = {}
            for version in versions:

                marking = Marking.objects.get(
                    participant=participant, version=version, marking_meta=meta
                )

                if version == "D":
                    pass
                elif (
                    version == "F"
                    and marking_action.status >= MarkingAction.LOCKED_BY_MODERATION
                ):
                    pass
                elif (
                    version == "O"
                    and question.exam.marking_delegation_can_see_organizer_marks
                    >= Exam.MARKING_DELEGATION_VIEW_WHEN_SUBMITTED
                    and (
                        marking_action.status >= MarkingAction.SUBMITTED_FOR_MODERATION
                        or question.exam.marking_delegation_can_see_organizer_marks
                        >= Exam.MARKING_DELEGATION_VIEW_YES
                    )
                ):
                    pass
                else:
                    marking = EmptyMarking(None, "")

                version_dict[version] = marking

            empty = EmptyMarking(None, "")
            version_dict["diff_color"] = get_diff_color_pair(
                version_dict.get("O", empty).points, version_dict.get("D", empty).points
            )
            participant_list.append((participant, version_dict))
        grouped_markings.append((meta, participant_list))

    documents = Document.objects.for_user(request.user).filter(
        position=question.position, participant__in=participants
    )

    ctx["documents"] = documents
    ctx["markings"] = grouped_markings
    ctx["sums"] = [
        {
            version: sum_if_not_none(
                entry[1][participant][1][version].points for entry in grouped_markings
            )
            or "-"
            for version in ["O", "D", "F"]
        }
        for participant in range(len(participants))
    ]
    return render(request, "ipho_marking/delegation_detail_all.html", ctx)


@permission_required("ipho_core.is_delegation")
def delegation_confirm(
    request, question_id, final_confirmation=False
):  # pylint: disable=too-many-locals, too-many-return-statements, too-many-branches, too-many-statements
    delegation = Delegation.objects.get(members=request.user)
    question = get_object_or_404(
        Question.objects.for_user(request.user),
        id=question_id,
    )
    form_error = ""

    marking_action, __ = MarkingAction.objects.get_or_create(
        question=question, delegation=delegation
    )

    if not question.exam.delegation_can_submit_marking():
        # delegation needs to be able to submit
        return HttpResponseRedirect(reverse("marking:delegation-summary"))

    if not final_confirmation and not marking_action.in_progress():
        # can only confirm open actions
        return HttpResponseRedirect(reverse("marking:delegation-summary"))

    if final_confirmation:
        if not question.exam.delegation_can_finalize_marking():
            # delegation needs to be able to finalize
            return HttpResponseRedirect(reverse("marking:delegation-summary"))

        if marking_action.in_progress():
            # open markings can only be submitted
            return HttpResponseRedirect(reverse("marking:delegation-summary"))

        if (
            not settings.SIGN_OFF_FINAL_MARKS
            and marking_action.status == MarkingAction.LOCKED_BY_MODERATION
        ):
            # if sign off is deactivated, locked marks cannot (don't need to be) signed off
            return HttpResponseRedirect(reverse("marking:delegation-summary"))
        if (
            not settings.ACCEPT_MARKS_BEFORE_MODERATION
            and not marking_action.status == MarkingAction.LOCKED_BY_MODERATION
        ):
            # if not settings.ACCEPT_MARKS_BEFORE_MODERATION only locked marks can be final-confirmed
            return HttpResponseRedirect(reverse("marking:delegation-summary"))

    if marking_action.status == MarkingAction.FINAL:
        # final marks cannot be confirmed in any case
        return HttpResponseRedirect(reverse("marking:delegation-summary"))

    if final_confirmation:
        if marking_action.status == MarkingAction.LOCKED_BY_MODERATION:
            vid = "F"
        elif marking_action.status == MarkingAction.SUBMITTED_FOR_MODERATION:
            vid = "O"
        else:
            return HttpResponseForbidden("An error occured, please contact support!")
        ptqueryset = Marking.objects.filter(  # Note that there is no for_user(), as the delegations will only see the checksum, this is not a problem
            marking_meta__question=question,
            participant__delegation=delegation,
            version=vid,
        ).values_list(
            "points"
        )
        ptlist = [str(p[0]) for p in ptqueryset]
        ptstr = str(ptlist)
        checksum = md5(ptstr.encode("ascii")).hexdigest()
    else:
        vid = "D"
        checksum = None
    # questions = Question.objects.filter(exam=exam, type=Question.ANSWER)
    metas_query = MarkingMeta.objects.filter(question=question)
    markings_query = Marking.objects.for_user(request.user, vid).filter(
        participant__delegation=delegation,
        marking_meta__in=metas_query,
    )

    all_markings_query = Marking.objects.filter(
        participant__delegation=delegation, marking_meta__in=metas_query, version=vid
    )

    # if some markings are not visible, we cannot continue
    if list(markings_query.all()) != list(all_markings_query.all()):
        if final_confirmation:
            raise Http404(
                f"Cannot confirm marks for {question.name}. Official markings are not yet published."
            )
        raise ValueError(f"Cannot confirm marks for {question.name}.")

    empty_markings_present = any(m.points is None for m in markings_query)
    if empty_markings_present:
        msg = None
        if (
            final_confirmation
            and marking_action.status == MarkingAction.LOCKED_BY_MODERATION
        ):  # if status is LOCKED_BY_MODERATION, all final marks should be there.
            msg = f"Some final marks for {question.name} are missing, please contact support!"
        elif (
            final_confirmation
        ):  # id status is OPEN or SUBMITTED_FOR_MODERATION, the orgainzer marks should be finished, but maybe aren't
            msg = "Some marks for {} are missing, please wait for the organizers to submit all marks!".format(
                question.name
            )
        elif not ALLOW_MARKS_NONE:
            msg = "Some marks for {} are missing, please submit marks for all subquestions and participants before confirming!".format(
                question.name
            )

        if msg:
            raise Http404(msg)

    error_messages = []
    if request.POST:  # pylint: disable=too-many-nested-blocks
        if "agree-submit" in request.POST and not "reject-final" in request.POST:
            if final_confirmation:
                if not "checksum" in request.POST:
                    msg = "Something went wrong (checksum missing), please contact support!"
                    return HttpResponseForbidden(msg)
                if request.POST["checksum"] != checksum:
                    error_msg = (
                        f"The marks for {question.name} have been changed. "
                        + "Please reload the page and check the marks again. "
                        + '<a href="{}" class="btn btn-default btn-xs">Reload</a>'.format(
                            reverse(
                                "marking:delegation-final-confirm", args=(question_id,)
                            )
                        )
                    )
                    error_messages.append(("alert-danger", error_msg))
                    checksum = "none"
                else:
                    if marking_action.status == MarkingAction.SUBMITTED_FOR_MODERATION:
                        for off_mark in Marking.objects.filter(
                            marking_meta__question=question,
                            participant__delegation=delegation,
                            version="O",
                        ):
                            fin_mark, __ = Marking.objects.get_or_create(
                                marking_meta=off_mark.marking_meta,
                                participant=off_mark.participant,
                                version="F",
                            )
                            fin_mark.points = off_mark.points
                            fin_mark.comment = off_mark.comment
                            fin_mark.save()
                    marking_action.status = MarkingAction.FINAL
                    marking_action.save()
                    return HttpResponseRedirect(reverse("marking:delegation-summary"))
            else:
                marking_action.status = MarkingAction.SUBMITTED_FOR_MODERATION
                marking_action.save()
                return HttpResponseRedirect(reverse("marking:delegation-summary"))
        elif "reject-final" in request.POST and final_confirmation:
            # i.e. if delegation rejects final marks, unlock marking action
            marking_action.status = MarkingAction.SUBMITTED_FOR_MODERATION
            marking_action.save()
            return HttpResponseRedirect(reverse("marking:delegation-summary"))
        else:
            form_error = "<strong>Error:</strong> You have to confirm the marking before continuing."

    metas = {
        k: list(g)
        for k, g in itertools.groupby(metas_query, key=lambda m: m.question.pk)
    }
    markings = {
        k: list(sorted(g, key=lambda m: m.marking_meta.pk))
        for k, g in itertools.groupby(
            markings_query, key=lambda m: m.marking_meta.question.pk
        )
    }
    participants = Participant.objects.filter(
        delegation=delegation, exam=question.exam
    ).all()
    # totals is of the form {question.pk:{participant.pk:total, ...}, ...}
    totals_questions = {
        k: {  # s is a list of markings for participant p
            p: sum_if_not_none(m.points for m in s)
            for p, s in itertools.groupby(
                sorted(g, key=lambda m: m.participant.pk),
                key=lambda m: m.participant.pk,
            )
        }
        for k, g in itertools.groupby(
            markings_query, key=lambda m: m.marking_meta.question.pk
        )
    }

    totals = {
        p: (sum_if_not_none(totals_questions[k][p] for k in totals_questions))
        for p in list(totals_questions.values())[0]
    }

    ctx = {
        "exam": question.exam,
        "questions": (question,),
        "markings": markings,
        "metas": metas,
        "participants": participants,
        "totals_questions": totals_questions,
        "totals": totals,
        "form_error": form_error,
        "error_messages": error_messages,
        "checksum": checksum,
    }
    if final_confirmation:
        ctx["confirmation_h2"] = f"Sign off final points for {question.name}"
        ctx["confirmation_info"] = (
            "Please check the points displayed below. "
            + "Note that you <strong>cannot</strong> moderate the points if you accept them now."
        )
        ctx["confirmation_checkbox_label"] = "I accept the final markings."
        ctx["confirm_button_label"] = "Accept"

        if marking_action.status == MarkingAction.LOCKED_BY_MODERATION:
            # i.e. if moderation has happened
            ctx["confirmation_info"] = (
                "Please check the points displayed below. "
                + f"If the points are not as discussed in the {_('moderation')}, "
                + "you can reopen it to allow the organizers to change the marks. "
                + f"Note that this does <strong>not</strong> lead to another {_('moderation')} session."
            )
            ctx["confirmation_alert_class"] = "alert-info"
            ctx["reject_button_label"] = f"Reopen {_('moderation')}"
        else:
            ctx["confirmation_alert_class"] = "alert-warning"

    else:
        ctx["confirmation_h2"] = f"Confirm points for {question.name}"
        ctx[
            "confirmation_info"
        ] = f"You need to confirm the marking of your delegation in order to attend the {_('moderation')} or to be able to indicate that you accept the marks without {_('moderation')} in a next step."
        ctx["confirmation_checkbox_label"] = "I confirm my version of the markings."
        if empty_markings_present:
            ctx["confirmation_checkbox_label"] = mark_safe(
                "<b>Some markings are empty!</b> I nonetheless confirm my version of the markings."
            )
            ctx["confirmation_alert_class"] = "alert-danger"
        ctx["confirm_button_label"] = "Confirm"
    return render(request, "ipho_marking/delegation_confirm.html", ctx)


@permission_required("ipho_core.is_marker")
def moderation_index(request, question_id=None):
    questions = Question.objects.for_user(request.user).filter(
        exam__moderation__gte=Exam.MODERATION_OPEN, type=Question.ANSWER
    )
    question = (
        None if question_id is None else get_object_or_404(Question, id=question_id)
    )
    if question is not None:
        free_actions = (
            MarkingAction.objects.filter(question=question)
            .filter(
                Q(status=MarkingAction.OPEN)
                | Q(status=MarkingAction.SUBMITTED_FOR_MODERATION)
            )
            .values("delegation_id")
        )
        delegations = (
            Delegation.objects.filter(id__in=free_actions)
            .exclude(name=OFFICIAL_DELEGATION)
            .all()
        )
    else:
        delegations = Delegation.objects.all()
    ctx = {"questions": questions, "question": question, "delegations": delegations}
    return render(request, "ipho_marking/moderation_index.html", ctx)


@permission_required("ipho_core.is_marker")
def moderation_detail(
    request, question_id, delegation_id
):  # pylint: disable=too-many-locals
    question = get_object_or_404(
        Question.objects.for_user(request.user),
        id=question_id,
        exam__moderation=Exam.MODERATION_OPEN,
    )
    delegation = get_object_or_404(Delegation, id=delegation_id)

    marking_action = get_object_or_404(
        MarkingAction, delegation=delegation, question=question
    )
    if marking_action.status in (
        MarkingAction.LOCKED_BY_MODERATION,
        MarkingAction.FINAL,
    ):
        raise Http404("These markings are locked, you cannot modify them!")

    metas = MarkingMeta.objects.filter(question=question)
    participants = delegation.get_participants(question.exam)

    participant_forms = []
    marking_forms = []
    all_valid = True
    with_errors = False
    # Note that neither for_user or editable are used for Markings
    # The reason is that upon moderation, all marks should be visible, and final marks are editable
    markings = Marking.objects.filter(marking_meta__in=metas)
    for i, participant in enumerate(participants):
        markings_official = markings.filter(participant=participant, version="O")
        markings_delegation = markings.filter(participant=participant, version="D")

        diff_color = []
        for off, dele in zip(markings_official, markings_delegation):
            diff_color.append(get_diff_color_pair(off.points, dele.points))

        FormSet = modelformset_factory(  # pylint: disable=invalid-name
            Marking,
            form=PointsForm,
            fields=["points", "comment"],
            extra=0,
            can_delete=False,
            can_order=False,
        )
        form = FormSet(
            request.POST or None,
            prefix=f"ppnt-{participant.pk}",
            queryset=Marking.objects.filter(
                marking_meta__in=metas, participant=participant, version="F"
            ),
            form_kwargs={"require_points": True},
        )
        for j, f in enumerate(form):
            f.fields["points"].widget.attrs["tabindex"] = i * len(metas) + j + 1
            f.fields["points"].widget.attrs["style"] = "width:60px"

        # TODO: accept only submission without None
        all_valid = all_valid and form.is_valid()
        with_errors = with_errors or form.errors

        participant_forms.append(
            (
                participant,
                form,
                markings_official,
                sum(
                    (m.points for m in markings_official if m.points is not None),
                    decimal.Decimal(0),
                ),
                sum(
                    (m.points for m in markings_delegation if m.points is not None),
                    decimal.Decimal(0),
                ),
            )
        )

        marking_forms.append(
            zip(markings_official, markings_delegation, diff_color, form)
        )

    if all_valid:
        for _, form, _, _, _ in participant_forms:
            form.save()
        if settings.SIGN_OFF_FINAL_MARKS:
            marking_action.status = MarkingAction.LOCKED_BY_MODERATION
        else:
            # if sign off is deactivated, jump directly to final (note that this also locks the moderation!)
            marking_action.status = MarkingAction.FINAL
        marking_action.save()
        return HttpResponseRedirect(
            reverse(
                "marking:moderation-confirmed",
                kwargs={"question_id": question.pk, "delegation_id": delegation.pk},
            )
        )

    scan_files_ready = (
        Document.objects.scans_ready(request.user)
        .filter(participant__exam=question.exam, position=question.position)
        .filter(participant__delegation=delegation)
        .values_list("participant__pk", flat=True)
    )

    # TODO: display errors
    ctx = {
        "question": question,
        "delegation": delegation,
        "participant_forms": participant_forms,
        "marking_forms": list(zip(metas, zip(*marking_forms))),
        "request": request,
        "max_points_sum": sum(m.max_points for m in metas),
        "scan_files_ready": scan_files_ready,
    }
    return render(request, "ipho_marking/moderation_detail.html", ctx)


@permission_required("ipho_core.is_marker")
def official_marking_index(request, question_id=None):
    questions = (
        Question.objects.for_user(request.user)
        .filter(type=Question.ANSWER)
        .filter(
            exam__marking_organizer_can_enter__gte=Exam.MARKING_ORGANIZER_CAN_ENTER_IF_NOT_SUBMITTED
        )
    )
    question = (
        None if question_id is None else get_object_or_404(questions, id=question_id)
    )
    error_msg = None
    form = None
    if question is not None:
        can_edit_submitted = (
            question.exam.marking_organizer_can_enter
            >= Exam.MARKING_ORGANIZER_CAN_ENTER_IF_NOT_FINAL
        )
        if can_edit_submitted:
            status_q = Q(status=MarkingAction.OPEN) | Q(
                status=MarkingAction.SUBMITTED_FOR_MODERATION
            )
        else:
            status_q = Q(status=MarkingAction.OPEN)

        free_actions = (
            MarkingAction.objects.filter(question=question)
            .filter(status_q)
            .values("delegation_id")
        )
        delegations = (
            Delegation.objects.filter(id__in=free_actions)
            .exclude(name=OFFICIAL_DELEGATION)
            .all()
        )
        if request.method == "POST":  # file uploaded
            form = UploadMarkingForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES["file"]
                try:
                    student_codes = import_marking(question.id, file)
                    context = {"question": question, "students": student_codes}
                    return render(
                        request,
                        "ipho_marking/official_marking_upload_confirmation.html",
                        context,
                    )
                except (pd.errors.ParserError, ValueError, AssertionError) as e:
                    error_msg = f"Invalid CSV file:\n{e}"
                    form.clean()
                    form = UploadMarkingForm()
        else:
            form = UploadMarkingForm()
    else:
        delegations = Delegation.objects.all()
    ctx = {
        "questions": questions,
        "question": question,
        "delegations": delegations,
        "form": form,
        "error_msg": error_msg,
    }
    return render(request, "ipho_marking/official_marking_index.html", ctx)


@permission_required("ipho_core.is_marker")
def create_marking_template(request, question_id):
    question = Question.objects.get(id=question_id)
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{question.name}.csv"'},
    )
    generate_template(question_id, response)
    return response


@permission_required("ipho_core.is_marker")
def official_marking_detail(request, question_id, delegation_id):
    question = get_object_or_404(
        Question.objects.for_user(request.user),
        id=question_id,
        exam__marking_organizer_can_enter__gte=Exam.MARKING_ORGANIZER_CAN_ENTER_IF_NOT_SUBMITTED,
    )
    delegation = get_object_or_404(Delegation, id=delegation_id)
    marking_action = get_object_or_404(
        MarkingAction, delegation=delegation, question=question
    )
    if marking_action.status == MarkingAction.FINAL:
        raise Http404("These markings are final, you cannot modify them!")

    metas = MarkingMeta.objects.filter(question=question)
    participants = delegation.get_participants(question.exam)

    marking_query = Marking.objects.editable(request.user, version="O").filter(
        marking_meta__in=metas, participant__in=participants
    )
    if not marking_query.exists():
        raise Http404("You cannot modify these markings!")

    participant_forms = []
    all_valid = True
    with_errors = False
    for i, participant in enumerate(participants):
        FormSet = modelformset_factory(  # pylint: disable=invalid-name
            Marking,
            form=PointsForm,
            fields=["points", "comment"],
            extra=0,
            can_delete=False,
            can_order=False,
        )
        form = FormSet(
            request.POST or None,
            prefix=f"ppnt-{participant.pk}",
            queryset=marking_query.filter(participant=participant),
        )
        for j, f in enumerate(form):
            f.fields["points"].widget.attrs["tabindex"] = i * len(metas) + j + 1
            f.fields["points"].widget.attrs["style"] = "width:100px"

        # TODO: accept only submission without None
        all_valid = all_valid and form.is_valid()
        with_errors = with_errors or form.errors

        participant_forms.append((participant, form))

    if all_valid:
        for _, form in participant_forms:
            form.save()
        return HttpResponseRedirect(
            reverse(
                "marking:official-marking-confirmed",
                kwargs={"question_id": question.pk, "delegation_id": delegation.pk},
            )
        )

    files_ready = {}
    files_ready["scan"] = (
        Document.objects.scans_ready(request.user)
        .filter(participant__exam=question.exam, position=question.position)
        .filter(participant__delegation=delegation)
        .values_list("participant__pk", flat=True)
    )

    files_ready["full_scan"] = (
        Document.objects.scans_ready(request.user)
        .filter(participant__exam=question.exam, position=question.position)
        .filter(participant__delegation=delegation)
        .exclude(
            scan_file_orig__isnull=True,
        )
        .exclude(scan_file_orig="")
        .values_list("participant__pk", flat=True)
    )

    # TODO: display errors
    ctx = {
        "question": question,
        "delegation": delegation,
        "participant_forms": participant_forms,
        "marking_forms": list(zip(metas, zip(*(f[1] for f in participant_forms)))),
        "request": request,
        "max_points_sum": sum(m.max_points for m in metas),
        "files_ready": files_ready,
        "show_name": SHOW_PARTICIPANT_NAME_TO_MARKERS,
    }
    return render(request, "ipho_marking/official_marking_detail.html", ctx)


@permission_required("ipho_core.is_marker")
def official_marking_confirmed(request, question_id, delegation_id):
    question = get_object_or_404(
        Question.objects.for_user(request.user),
        id=question_id,
    )
    delegation = get_object_or_404(Delegation, id=delegation_id)

    markings = (
        Marking.objects.for_user(request.user, version="O")
        .filter(marking_meta__question=question, participant__delegation=delegation)
        .values("participant")
        .annotate(total=Sum("points"))
        .values(
            "participant__pk",
            "total",
        )
    )

    markings_none_query = (
        Marking.objects.for_user(request.user, version="O")
        .filter(marking_meta__question=question, participant__delegation=delegation)
        .filter(points__isnull=True)
        .values_list("participant__pk")
    )
    markings_none = [pk[0] for pk in markings_none_query]

    for ppnt in markings:
        ppnt["participant"] = get_object_or_404(Participant, pk=ppnt["participant__pk"])

    ctx = {
        "question": question,
        "delegation": delegation,
        "markings": markings,
        "markings_none": markings_none,
        "show_name": SHOW_PARTICIPANT_NAME_TO_MARKERS,
    }
    return render(request, "ipho_marking/official_marking_confirmed.html", ctx)


@permission_required("ipho_core.is_marker")
def moderation_confirmed(request, question_id, delegation_id):
    question = get_object_or_404(
        Question,
        id=question_id,
        exam__visibility__gte=Exam.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT,
        exam__moderation=Exam.MODERATION_OPEN,
    )
    delegation = get_object_or_404(Delegation, id=delegation_id)

    markings = (
        Marking.objects.filter(
            marking_meta__question=question,
            version="F",
            participant__delegation=delegation,
        )
        .values("participant")
        .annotate(total=Sum("points"))
        .values(
            "participant__pk",
            "total",
        )
    )
    for ppnt in markings:
        ppnt["participant"] = get_object_or_404(Participant, pk=ppnt["participant__pk"])

    ctx = {"question": question, "delegation": delegation, "markings": markings}
    return render(request, "ipho_marking/moderation_confirmed.html", ctx)


@permission_required("ipho_core.is_organizer_admin")
def marking_submissions(request):
    countries_no_participants_exam = {}
    for exam in Exam.objects.for_user(request.user).all():
        countries_no_participants_exam[exam.pk] = (
            Delegation.objects.annotate(
                participant_count=Count("participant", filter=Q(participant__exam=exam))
            )
            .filter(participant_count=0)
            .values_list("country")
        )
    ctx = {
        "summaries": [
            (
                question.name,
                MarkingAction.objects.filter(
                    question=question, status=MarkingAction.OPEN
                )
                .exclude(
                    delegation__country__in=countries_no_participants_exam[
                        question.exam.pk
                    ]
                )
                .count(),
                MarkingAction.objects.filter(
                    question=question, status=MarkingAction.SUBMITTED_FOR_MODERATION
                )
                .exclude(
                    delegation__country__in=countries_no_participants_exam[
                        question.exam.pk
                    ]
                )
                .count(),
                MarkingAction.objects.filter(
                    question=question, status=MarkingAction.OPEN
                )
                .exclude(
                    delegation__country__in=countries_no_participants_exam[
                        question.exam.pk
                    ]
                )
                .values_list("delegation__country", flat=True),
                MarkingAction.objects.filter(
                    question=question, status=MarkingAction.LOCKED_BY_MODERATION
                )
                .exclude(
                    delegation__country__in=countries_no_participants_exam[
                        question.exam.pk
                    ]
                )
                .count(),
                MarkingAction.objects.filter(
                    question=question, status=MarkingAction.FINAL
                )
                .exclude(
                    delegation__country__in=countries_no_participants_exam[
                        question.exam.pk
                    ]
                )
                .count(),
                MarkingAction.objects.filter(
                    question=question,
                )
                .exclude(
                    delegation__country__in=countries_no_participants_exam[
                        question.exam.pk
                    ]
                )
                .exclude(status=MarkingAction.FINAL)
                .values_list("delegation__country", flat=True),
            )
            for question in Question.objects.for_user(request.user).filter(
                exam__marking_delegation_action__gte=Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT,
                type=Question.ANSWER,
            )
        ]
    }
    return render(request, "ipho_marking/marking_submissions.html", ctx)


@permission_required("ipho_core.is_organizer_admin")
def export_countries_to_moderate(request):
    csv_rows = []
    title_row = ["Code", "Country"]

    questions = Question.objects.for_user(request.user).filter(
        type=Question.ANSWER,
        exam__marking_delegation_action__gte=Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT,
    )
    for question in questions:
        title_row.append(f"{question.exam.code}-{question.position}")
    csv_rows.append(title_row)

    for delegation in Delegation.objects.exclude(name=OFFICIAL_DELEGATION):
        x = [delegation.name, delegation.country]
        for question in questions:
            for status in list(
                MarkingAction.objects.filter(
                    question=question, delegation=delegation
                ).values_list("status", flat=True)
            ):
                if status == MarkingAction.FINAL:
                    x.append("no")
                elif status in [MarkingAction.SUBMITTED_FOR_MODERATION]:
                    x.append("yes")
                elif status == MarkingAction.OPEN:
                    x.append("maybe")
                elif status == MarkingAction.LOCKED_BY_MODERATION:
                    x.append("no")

        csv_rows.append(x)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="countries-to-moderate.csv"'

    writer = csv.writer(response)
    writer.writerows(csv_rows)

    return response


def progress(request):
    vid = request.GET.get("version", "O")
    if request.user.has_perm("ipho_core.is_organizer_admin"):
        all_versions = Marking.MARKING_VERSIONS
    elif request.user.has_perm("ipho_core.is_marker"):
        all_versions = OrderedDict(
            [(k, v) for k, v in list(Marking.MARKING_VERSIONS.items()) if k != "D"]
        )
        if vid not in all_versions:
            return HttpResponseForbidden("Only the staff can see this page.")
    else:
        return HttpResponseForbidden("You do not have permission to access this page.")

    marking_statuses = []
    for exam in Exam.objects.for_user(request.user).all():
        participants = Participant.objects.filter(exam=exam).values("id", "code")
        questions = Question.objects.for_user(request.user).filter(
            exam=exam, type=Question.ANSWER
        )
        metas_groups = [
            MarkingMeta.objects.filter(question=question) for question in questions
        ]
        added = False
        for participant in participants:
            statuses = []
            for question, metas in zip(questions, metas_groups):
                # Note that the points are not visible, so no for_user is used
                # Also, we need to find all markings with points not null
                markings = Marking.objects.filter(
                    version=vid,
                    participant=participant["id"],
                    marking_meta__question=question,
                    points__isnull=False,
                )
                statuses.append(markings.count() < metas.count())
            if any(statuses):
                if not added:
                    marking_statuses.append([exam.name, questions, []])
                    added = True
                marking_statuses[-1][2].append((participant["code"], statuses))

    ctx = {
        "version": Marking.MARKING_VERSIONS[vid],
        "all_versions": all_versions,
        "marking_statuses": marking_statuses,
    }
    return render(request, "ipho_marking/progress.html", ctx)


@permission_required("ipho_core.is_organizer_admin")
def ranking(request):
    vid = "F"
    points_per_student = []
    markings = Marking.objects.for_user(request.user, vid)
    all_students = Student.objects.all()
    exams_final = Exam.objects.for_user(request.user).all()
    points_per_student = get_points_per_student(exams_final, all_students, markings)
    # Sort for ranking, rank students that have no final marks yet last
    points_per_student.sort(
        key=lambda x: (x is None, x[2] if x is not None else float("-inf")),
        reverse=True,
    )
    # We need a list of exams and total number of points for the header of the table
    exams_with_totals = [
        {
            "question__exam__name": exam.name,
            "exam_points": QuestionPointsRescale.min_max_points_for_exam(exam)[1],
        }
        for exam in exams_final
    ]

    ctx = {
        "final_points_exams": exams_with_totals,
        "points_per_student": points_per_student,
    }
    return render(request, "ipho_marking/ranking.html", ctx)


@permission_required("ipho_core.is_organizer_admin")
def export_ranking_csv(request):
    vid = "F"
    points_per_student = []
    markings = Marking.objects.for_user(request.user, vid)
    all_students = Student.objects.all()
    exams = Exam.objects.for_user(request.user).all()
    points_per_student = get_points_per_student(exams, all_students, markings)
    # Sort for ranking, rank students that have no final marks yet last
    points_per_student.sort(
        key=lambda x: (x is None, x[2] if x is not None else float("-inf")),
        reverse=True,
    )
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="ranking.csv"'

    writer = csv.writer(response)
    header = (
        ["Rank", "Student Code", "Student Name"]
        + [exam.name for exam in exams]
        + ["Total"]
    )
    writer.writerow(header)
    for idx, (student, exam_points, total) in enumerate(points_per_student):
        row = [str(idx + 1).zfill(3), student.code, student.full_name]
        row.extend(exam_points)
        row.append(total)
        writer.writerow(row)

    return response
