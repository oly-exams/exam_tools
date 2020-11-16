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

# pylint: disable=too-many-lines

import csv
import decimal
import itertools
from hashlib import md5
from collections import OrderedDict

from django.conf import settings
from django.db.models import Sum, F, Q
from django.urls import reverse
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, render
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    HttpResponseForbidden,
    Http404,
)
from django.contrib.auth.decorators import permission_required

from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, Document
from ipho_exam import qquery as qwquery
from ipho_exam import qml

from .models import MarkingMeta, Marking, MarkingAction
from .forms import ImportForm, PointsForm

OFFICIAL_LANGUAGE_PK = 1
OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")


@permission_required("ipho_core.is_organizer")
def import_exam(request):
    ctx = {}
    ctx["alerts"] = []
    form = ImportForm(request.POST or None)
    if form.is_valid():
        exam = form.cleaned_data["exam"]
        num_tot = 0
        num_created = 0
        num_marking_tot = 0
        num_marking_created = 0
        for question in exam.question_set.filter(type=Question.ANSWER):
            for delegation in Delegation.objects.exclude(
                name=OFFICIAL_DELEGATION
            ).all():
                MarkingAction.objects.get_or_create(
                    question=question, delegation=delegation
                )
            qwy = qwquery.latest_version(
                question_id=question.pk,
                lang_id=OFFICIAL_LANGUAGE_PK,
                user=request.user,
            )
            question_points = qml.question_points(qwy.qml)
            for i, (name, points) in enumerate(question_points):
                mmeta, created = MarkingMeta.objects.update_or_create(
                    question=question,
                    name=name,
                    defaults={"max_points": points, "position": i},
                )
                num_created += created
                num_tot += 1

                for student in Student.objects.all():
                    for version_id, _ in list(Marking.MARKING_VERSIONS.items()):
                        _, created = Marking.objects.get_or_create(
                            marking_meta=mmeta, student=student, version=version_id
                        )
                        num_marking_created += created
                        num_marking_tot += 1

        ctx["alerts"].append(
            '<div class="alert alert-success"><p><strong>Success.</strong></p><p>{} marking subquestion were imported.<p><ul><li>{} created</li><li>{} updated</li></ul><p>{} student marking created.</p><ul><li>{} student marking already found</li></ul></div>'.format(
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
def summary(request):
    vid = request.GET.get("version", "O")
    markings = Marking.objects.for_user(request.user).filter(version=vid)
    editable_markings = Marking.objects.editable(request.user).filter(version=vid)

    questions = (
        MarkingMeta.objects.for_user(request.user)
        .all()
        .values("question")
        .annotate(question_points=Sum("max_points"))
        .values(
            "question__pk", "question__exam__name", "question__name", "question_points"
        )
        .order_by("question__exam", "question__position")
        .distinct()
    )

    exams = (
        MarkingMeta.objects.for_user(request.user)
        .all()
        .values("question__exam")
        .annotate(exam_points=Sum("max_points"))
        .values("question__exam__pk", "question__exam__name", "exam_points")
        .order_by(
            "question__exam",
        )
        .distinct()
    )

    points_per_student = []
    students = Student.objects.all().values("id", "code", "delegation")
    for student in students:
        stud_question_points_list = []
        stud_question_editable_list = []
        for question in questions:
            stud_markings_question = markings.filter(
                marking_meta__question=question["question__pk"], student=student["id"]
            )
            points_question = stud_markings_question.aggregate(Sum("points"))[
                "points__sum"
            ]
            stud_question_points_list.append(points_question)

            editable = editable_markings.filter(
                marking_meta__question=question["question__pk"], student=student["id"]
            ).exists()
            if editable:
                stud_question_editable_list.append(question["question__pk"])
            else:
                stud_question_editable_list.append(False)

        stud_exam_points_list = []
        for exam in exams:
            stud_markings_exam = markings.filter(
                marking_meta__question__exam=exam["question__exam__pk"],
                student=student["id"],
            )
            points_exam = stud_markings_exam.aggregate(Sum("points"))["points__sum"]
            stud_exam_points_list.append(points_exam)

        points_per_student.append(
            (
                student,
                list(zip(stud_question_points_list, stud_question_editable_list)),
                stud_exam_points_list,
            )
        )

    context = {
        "vid": vid,
        "version": Marking.MARKING_VERSIONS[vid],
        "all_versions": Marking.MARKING_VERSIONS,
        "questions": questions,
        "points_per_student": points_per_student,
        "exams": exams,
    }
    return render(request, "ipho_marking/summary.html", context)


@permission_required("ipho_core.is_marker")
def staff_stud_detail(request, version, stud_id, question_id):
    ctx = {}
    ctx["msg"] = []

    if not request.user.has_perm("ipho_core.is_marker") or version != "O":
        raise Http404("You cannot modify these markings!")

    question = get_object_or_404(
        Question.objects.for_user(request.user), id=question_id
    )
    student = get_object_or_404(Student, id=stud_id)

    metas = MarkingMeta.objects.filter(question=question)
    marking_query = Marking.objects.editable(request.user).filter(
        marking_meta__in=metas, student=student, version=version
    )
    if not marking_query.exists():
        raise Http404("You cannot modify these markings!")

    FormSet = modelformset_factory(  # pylint: disable=invalid-name
        Marking,
        form=PointsForm,
        fields=["points"],
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
    ctx["student"] = student
    ctx["question"] = question
    ctx["exam"] = question.exam
    ctx["form"] = form
    return render(request, "ipho_marking/staff_edit.html", ctx)


@permission_required("ipho_core.is_organizer")
def export_with_total(request):
    return export(request, include_totals=True)


@permission_required("ipho_core.is_organizer")
def export(
    request, include_totals=False
):  # pylint: disable=too-many-locals, too-many-branches
    versions = request.GET.get("v", "O,D,F").split(",")

    csv_rows = []
    title_row = ["Student", "First_Name", "Last_Name", "Delegation", "Version"]
    mmeta = (
        MarkingMeta.objects.for_user(request.user)
        .all()
        .order_by("question__exam", "question__position", "position")
    )
    for meta in mmeta:
        title_row.append(f"{meta.question.name} - {meta.name} ({meta.max_points})")
    exams = Exam.objects.for_user(request.user)
    questions = (
        Question.objects.for_user(request.user)
        .filter(type=Question.ANSWER)
        .order_by("exam", "position")
    )
    if include_totals:
        for question in questions:

            title_row.append(f"Question Total: {question.exam.name} - {question.name}")
        for exam in exams:
            title_row.append(f"Exam Total: {exam.name}")
        title_row.append("Student Total")

    csv_rows.append(title_row)

    for student in Student.objects.all():
        stud_markings = Marking.objects.filter(student=student, marking_meta__in=mmeta)
        visible_stud_markings = Marking.objects.for_user(request.user).filter(
            student=student, marking_meta__in=mmeta
        )
        for version in versions:
            row = [
                student.code,
                student.first_name,
                student.last_name,
                student.delegation.name,
                version,
            ]

            version_markings = stud_markings.filter(version=version).order_by(
                "marking_meta__question__exam",
                "marking_meta__question__position",
                "marking_meta__position",
            )

            # directly iterating over is much simpler but a bit slower than using querysets
            points = []
            all_visible = True
            for marking in version_markings:
                if marking in visible_stud_markings:
                    points.append(marking.points)
                else:
                    all_visible = False
                    points.append(None)

            row += points
            if include_totals:
                for question in questions:
                    # Only append total if all markings are visible
                    q_markings = version_markings.filter(
                        marking_meta__question=question
                    )
                    # If some marks are not visible
                    if q_markings.exclude(pk__in=visible_stud_markings).exists():
                        row.append(None)
                    else:
                        row.append(_get_total(q_markings))

                for exam in exams:
                    # Only append total if all markings are visible
                    e_markings = version_markings.filter(
                        marking_meta__question__exam=exam
                    )
                    # If some marks are not visible
                    if e_markings.exclude(pk__in=visible_stud_markings).exists():
                        row.append(None)
                    else:
                        row.append(_get_total(e_markings))

                # Only append total if all markings are visible
                if all_visible:
                    student_total = _get_total(version_markings)
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
def delegation_export(request, exam_id=None):
    delegation = Delegation.objects.get(members=request.user)
    if exam_id is not None:
        exams = Exam.objects.for_user(request.user).filter(pk=exam_id)
    else:
        exams = Exam.objects.for_user(request.user)

    versions = request.GET.get("v", "O,D,F").split(",")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="markings.csv"'

    writer = csv.writer(response)
    students = Student.objects.filter(delegation=delegation)

    row1 = ["Student"]
    row2 = ["Version"]
    for student in students:
        for version in versions:
            row1.append(student.code)
            row2.append(Marking.MARKING_VERSIONS[version])
    writer.writerow(row1)
    writer.writerow(row2)
    totals = [decimal.Decimal(0)] * (len(row1) - 1)

    mmeta = (
        MarkingMeta.objects.for_user(request.user)
        .filter(question__exam__in=exams)
        .order_by("question__exam", "question__position", "position")
    )
    for meta in mmeta:
        row = [f"{meta.question.name} - {meta.name} ({meta.max_points})"]
        i = 0
        for student in students:
            for version in versions:
                marking = Marking.objects.for_user(request.user).filter(
                    student__delegation=delegation,
                    marking_meta=meta,
                    student=student,
                    version=version,
                )
                if marking.exists():
                    points = marking.first().points
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
    exams = Exam.objects.for_user(request.user).order_by("pk")
    students = Student.objects.filter(delegation=delegation)

    exam_marking_list = []
    exam_filter = Q(
        marking_delegation_action__gte=Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT
    ) | Q(
        marking_delegation_can_see_organizer_marks__gte=Exam.MARKING_DELEGATION_VIEW_WHEN_SUBMITTED
    )
    for exam in exams.filter(exam_filter):
        answer_sheet_list = Question.objects.filter(
            exam=exam, type=Question.ANSWER
        ).order_by("exam__pk", "position")

        student_list = []
        view_all = {a.pk: True for a in answer_sheet_list}
        edit_all = {a.pk: True for a in answer_sheet_list}

        # create the links for each student
        for student in students:
            student_ctx = {
                "pk": student.pk,
                "code": student.code,
                "first_name": student.first_name,
                "last_name": student.last_name,
            }
            question_list = []
            for question in answer_sheet_list:
                question_ctx = {"pk": question.pk}
                viewable_markings = Marking.objects.for_user(request.user).filter(
                    marking_meta__question=question, student=student
                )
                editable_markings = Marking.objects.editable(request.user).filter(
                    marking_meta__question=question, student=student
                )

                question_ctx["view"] = viewable_markings.exists()
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
                        ] = "Official marks are shown once you submitted your marks for moderation."
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

            student_ctx["questions"] = question_list
            student_list.append(student_ctx)
        question_list = []
        for question in answer_sheet_list:
            question_ctx = {
                "name": question.name,
                "pk": question.pk,
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
                    "text": "Submit marks",
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
                        "text": "Accept marks without moderation",
                        "tooltip": "You don't need to do anything if you want to have a moderation.",
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
                        "text": "Sign off marks",
                        "class": "btn-success",
                        "tooltip": "You can either accept the final marks or reopen the moderation again.",
                    }
            elif marking_status == MarkingAction.FINAL:
                action_button = {
                    "nolink": True,
                    "text": "Marks finalized",
                    "class": "btn-success",
                    "disabled": True,
                }
            actions = [
                action_button,
            ]
            question_ctx["actions"] = actions
            question_list.append(question_ctx)

        exam_ctxt = {
            "students": student_list,
            "questions": question_list,
            "name": exam.name,
            "pk": exam.pk,
        }
        exam_marking_list.append(exam_ctxt)

    # Final points pane
    vid = "F"
    points_per_student = []
    markings = Marking.objects.for_user(request.user).filter(version=vid)
    for student in students:
        # Exam points
        stud_exam_points_list = []
        for exam in exams:
            # if there are no open/submitted marking actions:
            if not MarkingAction.objects.filter(
                question__exam=exam,
                delegation=delegation,
                status__lte=MarkingAction.SUBMITTED_FOR_MODERATION,
            ).exists():
                stud_markings_exam = markings.filter(
                    marking_meta__question__exam=exam, student=student
                )
                points_exam = stud_markings_exam.aggregate(Sum("points"))["points__sum"]
                stud_exam_points_list.append(points_exam)
            else:
                stud_exam_points_list.append(None)

        not_none_pts = [p for p in stud_exam_points_list if p is not None]
        # As sum([]) = 0 would give a total =0 for None points, we need to set it to None by hand
        if not_none_pts and not_none_pts == stud_exam_points_list:
            total = sum([p for p in stud_exam_points_list if p is not None])
        else:
            total = None
        points_per_student.append((student, stud_exam_points_list, total))

    # We need a list of exams and total number of points for the header of the table
    exams_with_totals = (
        MarkingMeta.objects.filter(question__exam__in=exams)
        .values("question__exam")
        .annotate(exam_points=Sum("max_points"))
        .values("question__exam__name", "exam_points")
        .order_by(
            "question__exam",
        )
        .distinct()
    )

    # scans pane
    scans_table_per_exam = []
    scan_show_exams = Exam.objects.for_user(request.user).filter(
        delegation_scan_access__gte=Exam.DELEGATION_SCAN_ACCESS_STUDENT_ANSWER
    )
    for exam in scan_show_exams:
        questions = exam.question_set.filter(type=Question.ANSWER)
        scans_of_students = []
        for student in students:
            # Scans
            # Scans with status other than 'S' are skipped in the HTML
            # template. That is easier, because it allows correctly
            # continuing the table.
            stud_exam_scans_list = (
                Document.objects.for_user(request.user)
                .filter(student=student, exam=exam)
                .exclude(position=0)  # remove general instructions
                .order_by("position")
            )

            scans_of_students.append((student, stud_exam_scans_list))

        scans_table_per_exam.append((exam, questions, scans_of_students))

    ctx = {
        "delegation": delegation,
        "students": students,
        "exam_list": exam_marking_list,
        "final_points_exams": exams_with_totals,
        "points_per_student": points_per_student,
        "scans_table_per_exam": scans_table_per_exam,
    }
    return render(request, "ipho_marking/delegation_summary.html", ctx)


@permission_required("ipho_core.is_delegation")
def delegation_stud_edit(
    request, stud_id, question_id
):  # pylint: disable=too-many-locals
    delegation = Delegation.objects.get(members=request.user)
    student = get_object_or_404(Student, id=stud_id)
    if student.delegation != delegation:
        return HttpResponseForbidden(
            "You do not have permission to access this student."
        )

    question = get_object_or_404(
        Question.objects.for_user(request.user),
        id=question_id,
    )
    version = "D"

    ctx = {}
    ctx["msg"] = []
    ctx["student"] = student
    ctx["question"] = question
    ctx["exam"] = question.exam

    marking_action, _ = MarkingAction.objects.get_or_create(
        question=question, delegation=delegation
    )
    if not marking_action.in_progress():
        ctx["msg"].append(
            (
                ("alert-info"),
                "<strong>Note:</strong> The points have been submitted, you can no longer edit them.",
            )
        )
        return render(request, "ipho_marking/delegation_detail.html", ctx)

    metas = MarkingMeta.objects.filter(question=question)
    FormSet = modelformset_factory(  # pylint: disable=invalid-name
        Marking,
        form=PointsForm,
        fields=["points"],
        extra=0,
        can_delete=False,
        can_order=False,
    )
    form = FormSet(
        request.POST or None,
        queryset=Marking.objects.editable(request.user)
        .filter(marking_meta__in=metas, student=student, version=version)
        .order_by("marking_meta__position"),
    )
    if (
        question.exam.marking_delegation_can_see_organizer_marks
        >= Exam.MARKING_DELEGATION_VIEW_YES
    ):
        official_marking = {
            x.marking_meta_id: x
            for x in Marking.objects.filter(
                marking_meta__in=metas, student=student, version="O"
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
        students = delegation.student_set.all()
        stud_id_list = [str(s.id) for s in students]
        next_stud_index = stud_id_list.index(str(stud_id)) + 1
        next_stud_button = ""
        if next_stud_index < len(stud_id_list):
            next_stud_id = stud_id_list[next_stud_index]
            next_stud_button = (
                ' <a href="{}" class="btn btn-default btn-xs">next student</a> '.format(
                    reverse(
                        "marking:delegation-stud-detail-edit",
                        kwargs={"stud_id": next_stud_id, "question_id": question_id},
                    )
                )
            )

        ctx["msg"].append(
            (
                "alert-success",
                "<strong>Success.</strong> Points have been saved."
                + next_stud_button
                + ' <a href="{}#details" class="btn btn-default btn-xs">back to summary</a> '.format(
                    reverse("marking:delegation-summary")
                ),
            )
        )

    documents = Document.objects.for_user(request.user).filter(
        student=student, exam=question.exam, position=question.position
    )

    ctx["form"] = form
    ctx["documents"] = documents
    return render(request, "ipho_marking/delegation_detail.html", ctx)


@permission_required("ipho_core.is_delegation")
def delegation_edit_all(request, question_id):
    delegation = Delegation.objects.get(members=request.user)
    students = Student.objects.filter(delegation=delegation).order_by("code")

    question = get_object_or_404(
        Question.objects.for_user(request.user),
        id=question_id,
    )
    version = "D"

    ctx = {}
    ctx["msg"] = []
    ctx["students"] = students
    ctx["question"] = question
    ctx["exam"] = question.exam

    marking_action, _ = MarkingAction.objects.get_or_create(
        question=question, delegation=delegation
    )
    if not marking_action.in_progress():
        ctx["msg"].append(
            (
                ("alert-info"),
                "<strong>Note:</strong> The points have been submitted, you can no longer edit them.",
            )
        )
        return render(request, "ipho_marking/delegation_detail.html", ctx)

    metas = MarkingMeta.objects.filter(question=question).order_by("position")
    FormSet = modelformset_factory(  # pylint: disable=invalid-name
        Marking,
        form=PointsForm,
        fields=["points"],
        extra=0,
        can_delete=False,
        can_order=False,
    )
    formset = FormSet(
        request.POST or None,
        queryset=Marking.objects.editable(request.user)
        .filter(marking_meta__in=metas, student__in=students, version=version)
        .order_by("marking_meta__position", "student__code"),
    )

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

    documents = (
        Document.objects.for_user(request.user)
        .filter(exam=question.exam, position=question.position, student__in=students)
        .order_by("student__code")
    )

    ctx["documents"] = documents
    ctx["formset"] = formset
    return render(request, "ipho_marking/delegation_detail_all.html", ctx)


@permission_required("ipho_core.is_delegation")
def delegation_stud_view(request, stud_id, question_id):
    delegation = Delegation.objects.get(members=request.user)
    student = get_object_or_404(Student, id=stud_id)
    if student.delegation != delegation:
        return HttpResponseForbidden(
            "You do not have permission to access this student."
        )

    question = get_object_or_404(
        Question.objects.for_user(request.user), id=question_id
    )
    versions = ["O", "D", "F"]
    versions_display = [Marking.MARKING_VERSIONS[v] for v in versions]

    ctx = {}
    ctx["msg"] = []
    ctx["student"] = student
    ctx["question"] = question
    ctx["exam"] = question.exam
    ctx["versions_display"] = versions_display

    marking_action, _ = MarkingAction.objects.get_or_create(
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
    markings = (
        Marking.objects.for_user(request.user)
        .filter(marking_meta__in=metas, student=student, version__in=versions)
        .order_by("marking_meta")
    )

    grouped_markings = []
    for meta in metas:
        version_dict = {}
        for version in versions:
            marking = markings.filter(marking_meta=meta, version=version).first()
            if marking is not None:
                points = marking.points
            else:
                points = None
            version_dict[version] = points
        grouped_markings.append((meta, version_dict))

    documents = Document.objects.for_user(request.user).filter(
        student=student, exam=question.exam, position=question.position
    )

    ctx["documents"] = documents
    ctx["markings"] = grouped_markings
    return render(request, "ipho_marking/delegation_detail.html", ctx)


@permission_required("ipho_core.is_delegation")
def delegation_view_all(request, question_id):  # pylint: disable=too-many-locals
    delegation = Delegation.objects.get(members=request.user)
    students = Student.objects.filter(delegation=delegation)

    question = get_object_or_404(
        Question.objects.for_user(request.user),
        id=question_id,
    )
    versions = ["O", "D", "F"]
    versions_display = [Marking.MARKING_VERSIONS[v] for v in versions]

    ctx = {}
    ctx["msg"] = []
    ctx["question"] = question
    ctx["students"] = students
    ctx["exam"] = question.exam
    ctx["versions_display"] = versions_display

    marking_action, _ = MarkingAction.objects.get_or_create(
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
    markings = (
        Marking.objects.for_user(request.user)
        .filter(marking_meta__in=metas, student__in=students, version__in=versions)
        .order_by("marking_meta")
    )

    grouped_markings = []
    for meta in metas:
        student_list = []
        for student in students:
            version_dict = {}
            for version in versions:
                marking = markings.filter(
                    marking_meta=meta, version=version, student=student
                ).first()
                if marking is not None:
                    points = marking.points
                else:
                    points = None
                version_dict[version] = points
            student_list.append((student, version_dict))
        grouped_markings.append((meta, student_list))

    documents = Document.objects.for_user(request.user).filter(
        exam=question.exam, position=question.position, student__in=students
    )

    ctx["documents"] = documents
    ctx["markings"] = grouped_markings
    ctx["sums"] = [
        {
            version: sum(
                entry[1][student][1][version] or 0 for entry in grouped_markings
            )
            for version in ["O", "D", "F"]
        }
        for student in range(len(students))
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

    marking_action, _ = MarkingAction.objects.get_or_create(
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
        ptqueryset = (
            Marking.objects.filter(  # Note that there is no for_user(), as the delegations will only see the checksum, this is not a problem
                marking_meta__question=question,
                student__delegation=delegation,
                version=vid,
            )
            .order_by("pk")
            .values_list("points")
        )
        ptlist = [str(p[0]) for p in ptqueryset]
        ptstr = str(ptlist)
        checksum = md5(ptstr.encode("ascii")).hexdigest()
    else:
        vid = "D"
        checksum = None
    # questions = Question.objects.filter(exam=exam, type=Question.ANSWER)
    metas_query = MarkingMeta.objects.filter(question=question).order_by("position")
    markings_query = (
        Marking.objects.for_user(request.user)
        .filter(
            student__delegation=delegation, marking_meta__in=metas_query, version=vid
        )
        .order_by("marking_meta__position", "student")
    )

    markings_query = (
        Marking.objects.for_user(request.user)
        .filter(
            student__delegation=delegation, marking_meta__in=metas_query, version=vid
        )
        .order_by("marking_meta__position", "student")
    )
    all_markings_query = Marking.objects.filter(
        student__delegation=delegation, marking_meta__in=metas_query, version=vid
    ).order_by("marking_meta__position", "student")

    # if some markings are not visible, we cannot continue
    if list(markings_query) != list(all_markings_query):
        if final_confirmation:
            raise Http404(
                f"Cannot confirm marks for {question.name}. Official markings are not yet published."
            )
        raise ValueError(f"Cannot confirm marks for {question.name}.")

    if any(m.points is None for m in markings_query):
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
        else:
            msg = "Some marks for {} are missing, please submit marks for all subquestions and students before confirming!".format(
                question.name
            )

        raise Http404(msg)

    error_messages = []
    if request.POST:  # pylint: disable=too-many-nested-blocks
        if "agree-submit" in request.POST:
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
                            student__delegation=delegation,
                            version="O",
                        ):
                            fin_mark, _ = Marking.objects.get_or_create(
                                marking_meta=off_mark.marking_meta,
                                student=off_mark.student,
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
    students = Student.objects.filter(delegation=delegation).order_by("pk").all()
    # totals is of the form {question.pk:{student.pk:total, ...}, ...}
    totals_questions = {
        k: {  # s is a list of markings for student p
            p: sum(m.points for m in s)
            for p, s in itertools.groupby(
                sorted(g, key=lambda m: m.student.pk), key=lambda m: m.student.pk
            )
        }
        for k, g in itertools.groupby(
            markings_query, key=lambda m: m.marking_meta.question.pk
        )
    }

    totals = {
        p: sum(totals_questions[k][p] for k in totals_questions)
        for p in list(totals_questions.values())[0]
    }

    ctx = {
        "exam": question.exam,
        "questions": (question,),
        "markings": markings,
        "metas": metas,
        "students": students,
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
            + "Note that you <strong>cannot</strong> moderate the points if you acceppt them now."
        )
        ctx["confirmation_checkbox_label"] = "I accept the final markings."
        ctx["confirm_button_label"] = "Accept"

        if marking_action.status == MarkingAction.LOCKED_BY_MODERATION:
            # i.e. if moderation has happened
            ctx["confirmation_info"] = (
                "Please check the points displayed below. "
                + "If the points are not as discussed in the moderation, "
                + "you can reopen it to allow the organizers to change the marks. "
                + "Note that this does <strong>not</strong> lead to another moderation session."
            )
            ctx["confirmation_alert_class"] = "alert-info"
            ctx["reject_button_label"] = "Reopen moderation"
        else:
            ctx["confirmation_alert_class"] = "alert-warning"

    else:
        ctx["confirmation_h2"] = f"Confirm points for {question.name}"
        ctx[
            "confirmation_info"
        ] = "You need to confirm the marking of your delegation before you can see the points assigned by the official markers."
        ctx["confirmation_checkbox_label"] = "I confirm my version of the markings."
        ctx["confirm_button_label"] = "Confirm"
    return render(request, "ipho_marking/delegation_confirm.html", ctx)


@permission_required("ipho_core.is_marker")
def moderation_index(request, question_id=None):
    questions = (
        Question.objects.for_user(request.user)
        .filter(exam__moderation__gte=Exam.MODERATION_OPEN, type=Question.ANSWER)
        .order_by("exam__code", "position")
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
    if (
        marking_action.status == MarkingAction.LOCKED_BY_MODERATION
        or marking_action.status == MarkingAction.FINAL
    ):
        raise Http404("These markings are locked, you cannot modify them!")

    metas = MarkingMeta.objects.filter(question=question)
    students = delegation.student_set.all()

    student_forms = []
    marking_forms = []
    all_valid = True
    with_errors = False
    # Note that neither for_user or editable are used for Markings
    # The reason is that upon moderation, all marks should be visible, and final marks are editable
    markings = Marking.objects.filter(marking_meta__in=metas)
    for i, student in enumerate(students):
        markings_official = markings.filter(student=student, version="O").order_by(
            "marking_meta__position"
        )
        markings_delegation = markings.filter(student=student, version="D").order_by(
            "marking_meta__position"
        )

        FormSet = modelformset_factory(  # pylint: disable=invalid-name
            Marking,
            form=PointsForm,
            fields=["points"],
            extra=0,
            can_delete=False,
            can_order=False,
        )
        form = FormSet(
            request.POST or None,
            prefix=f"Stud-{student.pk}",
            queryset=Marking.objects.filter(
                marking_meta__in=metas, student=student, version="F"
            ),
        )
        for j, f in enumerate(form):
            f.fields["points"].widget.attrs["tabindex"] = i * len(metas) + j + 1
            f.fields["points"].widget.attrs["style"] = "width:60px"

        # TODO: accept only submission without None
        all_valid = all_valid and form.is_valid()
        with_errors = with_errors or form.errors

        student_forms.append(
            (
                student,
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
        marking_forms.append(zip(markings_official, markings_delegation, form))

    if all_valid:
        for _, form, _, _, _ in student_forms:
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
    # TODO: display errors
    ctx = {
        "question": question,
        "delegation": delegation,
        "student_forms": student_forms,
        "marking_forms": list(zip(metas, zip(*marking_forms))),
        "request": request,
        "max_points_sum": sum(m.max_points for m in metas),
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
        .order_by("exam__code", "position")
    )
    question = (
        None if question_id is None else get_object_or_404(questions, id=question_id)
    )
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
    else:
        delegations = Delegation.objects.all()
    ctx = {"questions": questions, "question": question, "delegations": delegations}
    return render(request, "ipho_marking/official_marking_index.html", ctx)


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
    if (
        marking_action.status == MarkingAction.LOCKED_BY_MODERATION
        or marking_action.status == MarkingAction.FINAL
    ):
        raise Http404("These markings are locked, you cannot modify them!")

    metas = MarkingMeta.objects.filter(question=question)
    students = delegation.student_set.all()

    student_forms = []
    all_valid = True
    with_errors = False
    for i, student in enumerate(students):
        FormSet = modelformset_factory(  # pylint: disable=invalid-name
            Marking,
            form=PointsForm,
            fields=["points"],
            extra=0,
            can_delete=False,
            can_order=False,
        )
        form = FormSet(
            request.POST or None,
            prefix=f"Stud-{student.pk}",
            queryset=Marking.objects.editable(request.user).filter(
                marking_meta__in=metas, student=student, version="O"
            ),
        )
        for j, f in enumerate(form):
            f.fields["points"].widget.attrs["tabindex"] = i * len(metas) + j + 1
            f.fields["points"].widget.attrs["style"] = "width:100px"

        # TODO: accept only submission without None
        all_valid = all_valid and form.is_valid()
        with_errors = with_errors or form.errors

        student_forms.append((student, form))

    if all_valid:
        for _, form in student_forms:
            form.save()
        return HttpResponseRedirect(
            reverse(
                "marking:official-marking-confirmed",
                kwargs={"question_id": question.pk, "delegation_id": delegation.pk},
            )
        )
    # TODO: display errors
    ctx = {
        "question": question,
        "delegation": delegation,
        "student_forms": student_forms,
        "marking_forms": list(zip(metas, zip(*(f[1] for f in student_forms)))),
        "request": request,
        "max_points_sum": sum(m.max_points for m in metas),
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
        Marking.objects.for_user(request.user)
        .filter(
            marking_meta__question=question, version="O", student__delegation=delegation
        )
        .values("student")
        .annotate(total=Sum("points"))
        .order_by("student")
        .values("student__first_name", "student__last_name", "student__code", "total")
    )

    ctx = {"question": question, "delegation": delegation, "markings": markings}
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
            marking_meta__question=question, version="F", student__delegation=delegation
        )
        .values("student")
        .annotate(total=Sum("points"))
        .order_by("student")
        .values("student__first_name", "student__last_name", "student__code", "total")
    )

    ctx = {"question": question, "delegation": delegation, "markings": markings}
    return render(request, "ipho_marking/moderation_confirmed.html", ctx)


@permission_required("ipho_core.is_organizer")
def marking_submissions(request):
    ctx = {
        "summaries": [
            (
                question.name,
                MarkingAction.objects.filter(
                    question=question, status=MarkingAction.OPEN
                )
                .exclude(delegation__name=OFFICIAL_DELEGATION)
                .count(),
                MarkingAction.objects.filter(
                    question=question, status=MarkingAction.SUBMITTED_FOR_MODERATION
                )
                .exclude(delegation__name=OFFICIAL_DELEGATION)
                .count(),
                MarkingAction.objects.filter(
                    question=question, status=MarkingAction.OPEN
                )
                .exclude(delegation__name=OFFICIAL_DELEGATION)
                .values_list("delegation__country", flat=True),
                MarkingAction.objects.filter(
                    question=question, status=MarkingAction.LOCKED_BY_MODERATION
                )
                .exclude(delegation__name=OFFICIAL_DELEGATION)
                .count(),
                MarkingAction.objects.filter(
                    question=question, status=MarkingAction.FINAL
                )
                .exclude(delegation__name=OFFICIAL_DELEGATION)
                .count(),
                MarkingAction.objects.filter(
                    question=question,
                )
                .exclude(delegation__name=OFFICIAL_DELEGATION)
                .exclude(status=MarkingAction.FINAL)
                .order_by("delegation__country")
                .values_list("delegation__country", flat=True),
            )
            for question in Question.objects.for_user(request.user)
            .filter(
                exam__marking_delegation_action__gte=Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT,
                type=Question.ANSWER,
            )
            .order_by("exam__pk", "position")
        ]
    }
    return render(request, "ipho_marking/marking_submissions.html", ctx)


@permission_required("ipho_core.is_organizer")
def export_countries_to_moderate(request):
    csv_rows = []
    title_row = ["Country", "Code"]

    questions = (
        Question.objects.for_user(request.user)
        .filter(type=Question.ANSWER)
        .order_by("exam", "position")
    )
    for question in questions:
        title_row.append(f"{question.exam.code}-{question.position}")
    csv_rows.append(title_row)

    for delegation in Delegation.objects.exclude(name=OFFICIAL_DELEGATION).order_by(
        "country"
    ):
        x = [delegation.country, delegation.name]
        for question in (
            Question.objects.for_user(request.user)
            .filter(
                exam__marking_delegation_action__gte=Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT,
                type=Question.ANSWER,
            )
            .order_by("exam__pk", "position")
        ):
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
    if request.user.has_perm("ipho_core.is_organizer"):
        all_versions = Marking.MARKING_VERSIONS
    elif request.user.has_perm("ipho_core.is_marker"):
        all_versions = OrderedDict(
            [(k, v) for k, v in list(Marking.MARKING_VERSIONS.items()) if k != "D"]
        )
        if vid not in all_versions:
            return HttpResponseForbidden("Only the staff can see this page.")
    else:
        return HttpResponseForbidden("You do not have permission to access this page.")

    students = Student.objects.all().values("id", "code")

    marking_statuses = []
    for exam in Exam.objects.for_user(request.user).all():
        questions = Question.objects.for_user(request.user).filter(
            exam=exam, type=Question.ANSWER
        )
        metas_groups = [
            MarkingMeta.objects.filter(question=question) for question in questions
        ]
        added = False
        for student in students:
            statuses = []
            for question, metas in zip(questions, metas_groups):
                # Note that the points are not visible, so no for_user is used
                # Also, we need to find all markings with points not null
                markings = Marking.objects.filter(
                    version=vid,
                    student=student["id"],
                    marking_meta__question=question,
                    points__isnull=False,
                )
                statuses.append(markings.count() < metas.count())
            if any(statuses):
                if not added:
                    marking_statuses.append([exam.name, questions, []])
                    added = True
                marking_statuses[-1][2].append((student["code"], statuses))

    ctx = {
        "version": Marking.MARKING_VERSIONS[vid],
        "all_versions": all_versions,
        "marking_statuses": marking_statuses,
    }
    return render(request, "ipho_marking/progress.html", ctx)
