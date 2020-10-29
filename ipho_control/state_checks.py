# This file contains all conditions for transitions
from ipho_exam.models import ExamAction
from ipho_marking.models import MarkingAction


def true_condition(exam):  # pylint: disable=unused-argument
    """A check that always passes."""
    return {"passed": True, "message": ""}


def all_translations_submitted(exam):  # pylint: disable=unused-argument
    """Check whether all translations are submitted."""
    unsubmitted_actions = ExamAction.objects.filter(
        action=ExamAction.TRANSLATION
    ).exclude(
        status=ExamAction.SUBMITTED,
    )
    count = unsubmitted_actions.count()
    if count > 4:
        return {
            "passed": False,
            "message": f"There are {count} unsubmitted translations",
        }
    if count:
        delegations = unsubmitted_actions.delegation.distinct().values_list(
            "name", flat=True
        )
        delegations = " ".join(delegations)
        return {
            "passed": False,
            "message": f"The following delegations have not submitted one or multiple exams: {delegations}",
        }
    return {"passed": True, "message": "All translations submitted."}


def exam_translations_submitted(exam):
    """Check whether all translations of corresponding exam are submitted."""
    unsubmitted_actions = ExamAction.objects.filter(
        action=ExamAction.TRANSLATION, exam=exam
    ).exclude(
        status=ExamAction.SUBMITTED,
    )
    count = unsubmitted_actions.count()
    if count > 4:
        return {
            "passed": False,
            "message": f"There are {count} unsubmitted translations",
        }
    if count:
        delegations = unsubmitted_actions.delegation.distinct().values_list(
            "name", flat=True
        )
        delegations = " ".join(delegations)
        return {
            "passed": False,
            "message": f"The following delegations have not yet submitted: {delegations}",
        }
    return {"passed": True, "message": "All translations submitted."}


# TODO
def all_markings_status(exam, status):  # pylint: disable=unused-argument
    """Check whether all markings have a given status."""
    return not MarkingAction.objects.exclude(status=status).exists()


# TODO
def exam_markings_status(exam, status):
    """Check whether all markings of corresponding exam have a given status."""
    return (
        not MarkingAction.objects.filter(question__exam=exam)
        .exclude(status=status)
        .exists()
    )
