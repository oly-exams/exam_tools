from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import Count

from ipho_control.models import ExamStateTransition
from ipho_exam.models import ExamAction, Exam


def trigger_transitions(trigger_name, exams=None):
    if not exams:
        return
    triggerable_transitions = ExamStateTransition.objects.filter(
        trigger_transitions__has_key=trigger_name, from_state_exam__in=exams
    )
    if triggerable_transitions.exists():
        for transition in triggerable_transitions.order_by("name").all():
            if transition.is_applicable_automatic():
                transition.apply()


@receiver(pre_save, sender=ExamAction)
def all_translations_submitted(sender, **kwargs):  # pylint: disable=unused-argument
    if (
        not ExamAction.objects.filter(action=ExamAction.TRANSLATION)
        .exclude(status=ExamAction.SUBMITTED)
        .exists()
    ):
        # TODO: can we get the name of the trigger in a more dynamic way?
        trigger_transitions("all_translations_submitted", Exam.objects.all())


@receiver(pre_save, sender=ExamAction)
def one_exam_translations_submitted(
    sender, **kwargs
):  # pylint: disable=unused-argument
    # TODO: does this queryset work as expected
    submitted_actions_per_exam = (
        ExamAction.objects.filter(action=ExamAction.TRANSLATION)
        .exclude(status=ExamAction.SUBMITTED)
        .values("exam")
        .order_by("exam")
        .annotate(count=Count("exam"))
        .filter(count=0)
    )
    exams = []
    for action in submitted_actions_per_exam:
        exams.append(action.exam)

    # TODO: can we get the name of the trigger in a more dynamic way?
    trigger_transitions("all_translations_submitted", exams)
