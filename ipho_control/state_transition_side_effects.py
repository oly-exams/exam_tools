# This file contains all possible side effects for state transitions
# from ipho_exam.models import Exam, Question

from ipho_exam.models import Question


def empty_effect(exam):  # pylint: disable=unused-argument
    """An empty effect."""


def lock_all_feedbacks(exam):
    """Locks feedback of all questions of corresponding exam."""
    Question.objects.filter(exam=exam).update(feedback_active=False)
