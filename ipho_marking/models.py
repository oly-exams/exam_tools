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

import operator
from collections import OrderedDict
from functools import reduce

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save

from ipho_core.models import Delegation
from ipho_exam.models import Participant, Question, Exam
from ipho_exam import qquery as qwquery
from ipho_exam import qml

OFFICIAL_LANGUAGE_PK = 1
OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")


def generate_markings_from_exam(exam, user=None):
    num_tot = 0
    num_created = 0
    num_marking_tot = 0
    num_marking_created = 0
    for question in exam.question_set.filter(type=Question.ANSWER):
        for delegation in Delegation.objects.exclude(name=OFFICIAL_DELEGATION).all():
            MarkingAction.objects.get_or_create(
                question=question, delegation=delegation
            )
        qwy = qwquery.latest_version(
            question_id=question.pk,
            lang_id=OFFICIAL_LANGUAGE_PK,
            user=user,
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

            for participant in Participant.objects.all():
                for version_id, _ in list(Marking.MARKING_VERSIONS.items()):
                    _, created = Marking.objects.get_or_create(
                        marking_meta=mmeta, participant=participant, version=version_id
                    )
                    num_marking_created += created
                    num_marking_tot += 1
    return num_tot, num_created, num_marking_tot, num_marking_created


class MarkingActionManager(models.Manager):
    def get_by_natural_key(self, question_name, exam_name, delegation_name):
        question = Question.objects.get_by_natural_key(question_name, exam_name)
        return self.get(
            question=question,
            delegation=Delegation.objects.get_by_natural_key(delegation_name),
        )


class MarkingAction(models.Model):
    objects = MarkingActionManager()

    OPEN = 0
    SUBMITTED_FOR_MODERATION = 1
    LOCKED_BY_MODERATION = 2
    FINAL = 3
    STATUS_CHOICES = (
        (OPEN, "In progress"),
        (SUBMITTED_FOR_MODERATION, "Submitted"),
        (LOCKED_BY_MODERATION, "Locked"),
        (FINAL, "Final"),
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    delegation = models.ForeignKey(
        Delegation, related_name="marking_status", on_delete=models.CASCADE
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("question", "delegation"),)
        index_together = unique_together

    def natural_key(self):
        return self.question.natural_key() + self.delegation.natural_key()

    natural_key.dependencies = ["ipho_exam.question", "ipho_core.delegation"]

    def in_progress(self):
        return self.status == MarkingAction.OPEN

    @staticmethod
    def marking_in_progress(exam, delegation):
        marks_open = MarkingAction.objects.filter(
            question__exam=exam, delegation=delegation, status=MarkingAction.OPEN
        ).exists()
        return marks_open


@receiver(
    post_save,
    sender=Question,
    dispatch_uid="create_marking_actions_on_question_creation",
)
def create_actions_on_exam_creation(
    instance, created, raw, **kwargs
):  # pylint: disable=unused-argument
    # Ignore fixtures and saves for existing courses.
    if not created or raw or instance.type != Question.ANSWER:
        return
    for delegation in Delegation.objects.all():
        MarkingAction.objects.get_or_create(question=instance, delegation=delegation)


@receiver(
    post_save,
    sender=Delegation,
    dispatch_uid="create_marking_actions_on_delegation_creation",
)
def create_actions_on_delegation_creation(
    instance, created, raw, **kwargs
):  # pylint: disable=unused-argument
    # Ignore fixtures and saves for existing courses.
    if not created or raw:
        return
    for question in Question.objects.filter(type=Question.ANSWER).all():
        MarkingAction.objects.get_or_create(question=question, delegation=instance)


class MarkingMetaManager(models.Manager):
    def for_user(self, user):
        exams = Exam.objects.for_user(user)
        queryset = self.get_queryset().filter(question__exam__in=exams)
        return queryset


class MarkingMeta(models.Model):
    objects = MarkingMetaManager()

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    max_points = models.DecimalField(max_digits=8, decimal_places=2)
    position = models.PositiveSmallIntegerField(
        default=10, help_text="Sorting index inside one question"
    )

    def __str__(self):
        return f"{self.name} [{self.question.name}] {self.max_points} points"

    class Meta:
        ordering = ["position"]
        unique_together = index_together = (("question", "name"),)


class MarkingManager(models.Manager):
    def for_user(self, user):  # pylint: disable=too-many-locals
        # return self.get_queryset().filter(marking_meta__in=MarkingMeta.objects.for_user(user))
        exams = Exam.objects.for_user(user)
        queryset = self.get_queryset().filter(marking_meta__question__exam__in=exams)

        # In a first step, we need to find markings which are >=locked/submitted
        # We achieve this by creating individual Q objects for each Action and then concatenating them
        locked_actions = MarkingAction.objects.filter(
            status__gte=MarkingAction.LOCKED_BY_MODERATION
        )
        subm_actions = MarkingAction.objects.filter(
            status__gte=MarkingAction.SUBMITTED_FOR_MODERATION
        )
        locked_action_q_list = [
            Q(participant__delegation=a.delegation, marking_meta__question=a.question)
            for a in locked_actions
        ]
        subm_action_q_list = [
            Q(participant__delegation=a.delegation, marking_meta__question=a.question)
            for a in subm_actions
        ]
        # Q(pk__in=[]) is an empty Q object which we use as initializer (and default) object in reduce
        locked_action_q = reduce(operator.or_, locked_action_q_list, Q(pk__in=[]))
        subm_action_q = reduce(operator.or_, subm_action_q_list, Q(pk__in=[]))
        if user.is_superuser:
            return queryset
        if user.has_perm("ipho_core.is_marker") or user.has_perm(
            "ipho_core.is_organizer_admin"
        ):
            # This filters out all >=locked Delegation Markings for exams with Org view after moderation.
            exams_org_view_after_mod = exams.filter(
                marking_organizer_can_see_delegation_marks__gte=Exam.MARKING_ORGANIZER_VIEW_MODERATION_FINAL
            )
            deleg_marking_view_after_mod_q = (
                Q(marking_meta__question__exam__in=exams_org_view_after_mod)
                & Q(version="D")
                & locked_action_q
            )
            # This filters out all >=submitted Delegation Markings for exams with Org view after submission.
            exams_org_view_after_subm = exams.filter(
                marking_organizer_can_see_delegation_marks__gte=Exam.MARKING_ORGANIZER_VIEW_WHEN_SUBMITTED
            )
            deleg_marking_view_after_subm_q = (
                Q(marking_meta__question__exam__in=exams_org_view_after_subm)
                & Q(version="D")
                & subm_action_q
            )
            # This filters out all final, >= locked marks
            marking_final_q = Q(version="F") & locked_action_q
            # This filters out the official marks
            marking_official = Q(version="O")

            return queryset.filter(
                deleg_marking_view_after_mod_q
                | deleg_marking_view_after_subm_q
                | marking_final_q
                | marking_official
            )

        if user.has_perm("ipho_core.is_delegation"):
            # A delegation can only view their own markings
            delegs = Delegation.objects.filter(members=user)
            queryset = queryset.filter(participant__delegation__in=delegs)
            # This filters out all >=submitted Official Markings for exams with Delegation can view after submission.
            exams_deleg_view_after_subm = exams.filter(
                marking_delegation_can_see_organizer_marks__gte=Exam.MARKING_DELEGATION_VIEW_WHEN_SUBMITTED
            )
            org_marking_view_after_subm_q = (
                Q(marking_meta__question__exam__in=exams_deleg_view_after_subm)
                & Q(version="O")
                & subm_action_q
            )
            # This filters out all Official markings for exams with delegation can view off marks
            exams_deleg_view_yes = exams.filter(
                marking_delegation_can_see_organizer_marks__gte=Exam.MARKING_DELEGATION_VIEW_YES
            )
            org_marking_view_always_q = Q(
                marking_meta__question__exam__in=exams_deleg_view_yes
            ) & Q(version="O")
            # This filters out all final, >= locked marks
            marking_final_q = Q(version="F") & locked_action_q
            # This filters out the delegation marks
            marking_delegation = Q(version="D")

            return queryset.filter(
                org_marking_view_after_subm_q
                | org_marking_view_always_q
                | marking_final_q
                | marking_delegation
            )
        return self.none()

    def editable(self, user):
        queryset = self.for_user(user)
        exams = Exam.objects.for_user(user)

        # In a first step, we need to find markings which are <final/submitted
        # We achieve this by creating individual Q objects for each Action and then concatenating them
        un_final_actions = MarkingAction.objects.filter(status__lt=MarkingAction.FINAL)
        un_subm_actions = MarkingAction.objects.filter(
            status__lt=MarkingAction.SUBMITTED_FOR_MODERATION
        )
        un_final_action_q_list = [
            Q(participant__delegation=a.delegation, marking_meta__question=a.question)
            for a in un_final_actions
        ]
        un_subm_action_q_list = [
            Q(participant__delegation=a.delegation, marking_meta__question=a.question)
            for a in un_subm_actions
        ]
        # Q(pk__in=[]) is an empty Q object which we use as initializer (and default) object in reduce
        un_final_action_q = reduce(operator.or_, un_final_action_q_list, Q(pk__in=[]))
        un_subm_action_q = reduce(operator.or_, un_subm_action_q_list, Q(pk__in=[]))

        if user.is_superuser:
            # prevents superuser from accidentally editing something
            return self.none()
        if user.has_perm("ipho_core.is_marker"):
            # Organizers can only edit organizer Markings
            queryset = queryset.filter(version="O")

            # This filters out all <submitted Markings for exams with Org edit if not submitted
            exams_org_edit_before_subm = exams.filter(
                marking_organizer_can_enter__gte=Exam.MARKING_ORGANIZER_CAN_ENTER_IF_NOT_SUBMITTED
            )
            marking_edit_before_subm_q = (
                Q(marking_meta__question__exam__in=exams_org_edit_before_subm)
                & un_subm_action_q
            )
            # This filters out all <final Markings for exams with Org edit if not final
            exams_org_edit_before_final = exams.filter(
                marking_organizer_can_enter__gte=Exam.MARKING_ORGANIZER_CAN_ENTER_IF_NOT_FINAL
            )
            marking_edit_before_final_q = (
                Q(marking_meta__question__exam__in=exams_org_edit_before_final)
                & un_final_action_q
            )
            return queryset.filter(
                marking_edit_before_subm_q | marking_edit_before_final_q
            )

        if user.has_perm("ipho_core.is_delegation"):
            # Delegations should only be able to edit delegation markings
            queryset = queryset.filter(version="D")

            # This filters out all Markings for exams with Delegation action >= MARKING_DELEGATION_ACTION_ENTER_SUBMIT
            exams_deleg_edit = exams.filter(
                marking_delegation_action__gte=Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT
            )
            marking_deleg_edit_q = Q(marking_meta__question__exam__in=exams_deleg_edit)

            # Only unsubmitted markings can be edited
            return queryset.filter(marking_deleg_edit_q & un_subm_action_q)
        return self.none()


class Marking(models.Model):
    objects = MarkingManager()

    marking_meta = models.ForeignKey(MarkingMeta, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    points = models.DecimalField(
        null=True,
        blank=True,
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
    )
    comment = models.TextField(null=True, blank=True)
    MARKING_VERSIONS = OrderedDict(
        [
            ("O", "Organizers"),
            ("D", "Delegation"),
            ("F", "Final"),
        ]
    )
    version = models.CharField(max_length=1, choices=list(MARKING_VERSIONS.items()))

    def clean(self):
        try:
            if self.points > self.marking_meta.max_points:
                raise ValidationError(
                    {
                        "points": ValidationError(
                            "The number of points cannot exceed the maximum."
                        )
                    }
                )
        except TypeError:
            # pylint: disable=raise-missing-from
            raise ValidationError(
                {"points": ValidationError("The number of points must be a number.")}
            )

    def exam_question(self):
        return self.marking_meta.question

    def __str__(self):
        return (
            f"{self.marking_meta.name} [{self.points} / {self.marking_meta.max_points}]"
        )

    class Meta:
        # should probably have an ordering?
        unique_together = (("marking_meta", "participant", "version"),)
