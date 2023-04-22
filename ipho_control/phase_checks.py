# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
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


# This file contains all checks for phases

from django.conf import settings

from ipho_exam.models import ExamAction
from ipho_marking.models import MarkingAction

OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")


def true_condition(exam):  # pylint: disable=unused-argument
    """A check that always passes."""
    return {"passed": True, "message": "True check", "pretty": "Always True"}


def all_delegations_submitted(exam):  # pylint: disable=unused-argument
    """Checks whether all delegations have submitted."""
    pretty_name = "Translations submitted"
    unsubmitted_actions = (
        ExamAction.objects.filter(action=ExamAction.TRANSLATION)
        .exclude(
            status=ExamAction.SUBMITTED,
        )
        .exclude(
            delegation__name=OFFICIAL_DELEGATION,
        )
    )
    count = unsubmitted_actions.values("delegation").distinct().count()
    if count > 4:
        return {
            "passed": False,
            "message": f"There are {count} unsubmitted translations",
            "pretty": pretty_name,
        }
    if count:
        delegations = (
            unsubmitted_actions.values("delegation")
            .distinct()
            .values_list("delegation__name", flat=True)
        )
        delegations = " ".join(delegations)
        return {
            "passed": False,
            "pretty": pretty_name,
            "message": f"Unsubmitted documents! The following delegations have not submitted one or multiple exams: {delegations}",
        }
    return {
        "passed": True,
        "pretty": pretty_name,
        "message": "All translations submitted.",
    }


def exam_delegations_submitted(exam):
    """Checks whether all delegations have submitted the corresponding exam."""
    pretty_name = f"Translations submitted for {exam.name}"
    unsubmitted_actions = (
        ExamAction.objects.filter(action=ExamAction.TRANSLATION, exam=exam)
        .exclude(
            status=ExamAction.SUBMITTED,
        )
        .exclude(
            delegation__name=OFFICIAL_DELEGATION,
        )
    )
    count = unsubmitted_actions.count()
    if count > 4:
        return {
            "passed": False,
            "pretty": pretty_name,
            "message": f"There are {count} unsubmitted translations",
        }
    if count:
        delegations = (
            unsubmitted_actions.values("delegation")
            .distinct()
            .values_list("delegation__name", flat=True)
        )
        delegations = " ".join(delegations)
        return {
            "passed": False,
            "pretty": pretty_name,
            "message": f"Unsubmitted translations! The following delegations have not yet submitted: {delegations}",
        }
    return {
        "passed": True,
        "pretty": pretty_name,
        "message": "All translations submitted.",
    }


def markings_not_open(exam):  # pylint: disable=unused-argument
    """Checks whether no markings are open."""
    pretty_name = "All Markings submitted"
    actions = MarkingAction.objects.filter(status=MarkingAction.OPEN,).exclude(
        delegation__name=OFFICIAL_DELEGATION,
    )
    count = actions.count()
    if count > 4:
        return {
            "passed": False,
            "pretty": pretty_name,
            "message": f"There are {count} unsubmitted markings",
        }
    if count:
        delegations = (
            actions.values("delegation")
            .distinct()
            .values_list("delegation__name", "question__name")
        )
        del_quest_list = [f"{dl} - Question: {q}" for (dl, q) in delegations]
        marks = " ".join(del_quest_list)
        return {
            "passed": False,
            "pretty": pretty_name,
            "message": f"Unsubmitted Markings! The following markings have not yet been submitted: {marks}",
        }
    return {"passed": True, "pretty": pretty_name, "message": "All markings submitted."}


def exam_markings_not_open(exam):
    """Checks whether no markings are open for corresponding exam."""
    pretty_name = f"Markings submitted for {exam.name}"
    actions = MarkingAction.objects.filter(
        status=MarkingAction.OPEN, question__exam=exam
    ).exclude(
        delegation__name=OFFICIAL_DELEGATION,
    )
    count = actions.count()
    if count > 4:
        return {
            "passed": False,
            "pretty": pretty_name,
            "message": f"There are {count} unsubmitted markings",
        }
    if count:
        delegations = (
            actions.values("delegation")
            .distinct()
            .values_list("delegation__name", "question__name")
        )
        del_quest_list = [f"{dl} - Question: {q}" for (dl, q) in delegations]
        marks = " ".join(del_quest_list)
        return {
            "passed": False,
            "pretty": pretty_name,
            "message": f"Unsubmitted Markings! The following markings have not yet been submitted: {marks}",
        }
    return {"passed": True, "pretty": pretty_name, "message": "All markings submitted."}


def markings_finalized(exam):  # pylint: disable=unused-argument
    """Checks whether all markings are final for corresponding exam."""
    pretty_name = "All Markings final"
    actions = MarkingAction.objects.exclude(status=MarkingAction.FINAL,).exclude(
        delegation__name=OFFICIAL_DELEGATION,
    )
    count = actions.count()
    if count > 4:
        return {
            "passed": False,
            "pretty": pretty_name,
            "message": f"There are {count} markings not finalized.",
        }
    if count:
        delegations = (
            actions.values("delegation")
            .distinct()
            .values_list("delegation__name", "question__name")
        )
        del_quest_list = [f"{dl} - Question: {q}" for (dl, q) in delegations]
        marks = " ".join(del_quest_list)
        return {
            "passed": False,
            "pretty": pretty_name,
            "message": f"Unfinalized Markings! The following markings have not yet been finalized: {marks}",
        }
    return {"passed": True, "pretty": pretty_name, "message": "All markings submitted."}


def exam_markings_finalized(exam):
    """Checks whether all markings are final for corresponding exam."""
    pretty_name = f"Markings finalized for {exam.name}"
    actions = (
        MarkingAction.objects.filter(question__exam=exam)
        .exclude(
            delegation__name=OFFICIAL_DELEGATION,
        )
        .exclude(
            status=MarkingAction.FINAL,
        )
    )
    count = actions.count()
    if count > 4:
        return {
            "passed": False,
            "pretty": pretty_name,
            "message": f"There are {count} markings not finalized.",
        }
    if count:
        delegations = (
            actions.values("delegation")
            .distinct()
            .values_list("delegation__name", "question__name")
        )
        del_quest_list = [f"{dl} - Question: {q}" for (dl, q) in delegations]
        marks = " ".join(del_quest_list)
        return {
            "passed": False,
            "pretty": pretty_name,
            "message": f"Unfinalized Markings! The following markings have not yet been finalized: {marks}",
        }
    return {"passed": True, "pretty": pretty_name, "message": "All markings submitted."}
