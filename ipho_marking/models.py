import operator
from collections import OrderedDict
from functools import reduce

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from ipho_core.models import Delegation
from ipho_exam import qml
from ipho_exam import qquery as qwquery
from ipho_exam.models import Exam, Participant, Question

OFFICIAL_LANGUAGE_PK = 1
OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")
ALLOW_NEGATIVE_MARKS = getattr(settings, "ALLOW_NEGATIVE_MARKS", False)
ALLOW_MARKS_NONE = getattr(settings, "ALLOW_MARKS_NONE", False)


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
        total_points = 0
        for i, (name, min_points, max_points) in enumerate(question_points):
            mmeta, created = MarkingMeta.objects.update_or_create(
                question=question,
                name=name,
                defaults={
                    "min_points": min_points,
                    "max_points": max_points,
                    "position": i,
                },
            )
            total_points += max_points
            num_created += created
            num_tot += 1

            for participant in Participant.objects.filter(exam=exam):
                for version_id, _ in list(Marking.MARKING_VERSIONS.items()):
                    _, created = Marking.objects.get_or_create(
                        marking_meta=mmeta, participant=participant, version=version_id
                    )
                    num_marking_created += created
                    num_marking_tot += 1

        QuestionPointsRescale.objects.get_or_create(
            question=question,
        )

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
        ordering = ["question", "delegation"]

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
def create_actions_on_exam_creation(instance, created, raw, **kwargs):
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
def create_actions_on_delegation_creation(instance, created, raw, **kwargs):
    # Ignore fixtures and saves for existing courses.
    if not created or raw:
        return
    for question in Question.objects.filter(type=Question.ANSWER).all():
        MarkingAction.objects.get_or_create(question=question, delegation=instance)


class QuestionPointsRescaleManager(models.Manager):
    def for_user(self, user):
        exams = Exam.objects.for_user(user)
        queryset = self.get_queryset().filter(question__exam__in=exams)
        return queryset


def validate_nonzero(value):
    if value == 0:
        raise ValidationError("Field cannot be zero.")


def sum_if_not_none(iterable):
    if not iterable:
        return None
    return reduce(
        lambda x, y: x + y if (x is not None and y is not None) else None, iterable
    )


class QuestionPointsRescale(models.Model):
    objects = QuestionPointsRescaleManager()

    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    numerator = models.SmallIntegerField(default=1)
    denominator = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            validate_nonzero,
        ],
    )
    shift = models.DecimalField(default=0, max_digits=8, decimal_places=2)

    class Meta:
        unique_together = index_together = ("question",)
        ordering = ["question"]

    def __str__(self):
        return f"[Scale: {(self.numerator/self.denominator) if self.denominator else 'NaN'} - Shift: {self.shift}] {self.question.name}"

    def transform(self, value):
        if value is None:
            return None
        return value * self.numerator / self.denominator + self.shift

    @staticmethod
    def min_max_points_for_exam(exam):
        questions = (
            Question.objects.filter(exam=exam)
            .annotate(max_total=Sum("markingmeta__max_points"))
            .annotate(min_total=Sum("markingmeta__min_points"))
            .values("max_total", "min_total", "pk")
            .distinct()
        )
        max_points = []
        min_points = []

        for quest in questions:
            # points_total = quest.markingmeta_set.annotate(max_total=Sum("max_points")).annotate(min_total=Sum("min_points")).values("max_total", "min_total").distinct()
            qscale = QuestionPointsRescale.objects.filter(
                question__id=quest["pk"]
            ).first()
            if quest["min_total"] is None or quest["max_total"] is None:
                continue
            if not qscale:
                max_points.append(quest["max_total"])
                min_points.append(quest["min_total"])
                continue
            max_points.append(qscale.transform(quest["max_total"]))
            min_points.append(qscale.transform(quest["min_total"]))

        return sum_if_not_none(min_points), sum_if_not_none(max_points)

    @staticmethod
    def external_sum_for_exam(markings, participant_code=None, exam=None):
        if participant_code is not None and exam is not None:
            markings = markings.filter(
                marking_meta__question__exam=exam,
                participant__code=participant_code,
            )

        ppnt_markings_exam = markings.values("marking_meta__question").annotate(
            question_total=Sum("points")
        )

        points_exam = 0
        all_none = True
        for x in ppnt_markings_exam:
            qscale = QuestionPointsRescale.objects.filter(
                question__pk=x["marking_meta__question"]
            ).first()
            if x["question_total"] is not None:
                points_exam += qscale.transform(x["question_total"])
                all_none = False
        if all_none:
            return None
        return points_exam


class MarkingMetaManager(models.Manager):
    def for_user(self, user):
        exams = Exam.objects.for_user(user)
        queryset = self.get_queryset().filter(question__exam__in=exams)
        return queryset


class MarkingMeta(models.Model):
    objects = MarkingMetaManager()

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    min_points = models.DecimalField(
        null=True, blank=True, max_digits=8, decimal_places=2
    )
    max_points = models.DecimalField(
        null=True, blank=True, max_digits=8, decimal_places=2
    )
    position = models.PositiveSmallIntegerField(
        default=10, help_text="Sorting index inside one question"
    )

    def __str__(self):
        return f"{self.name} [{self.question.name}] ({self.max_points},{self.max_points}) points"

    class Meta:
        unique_together = index_together = (("question", "name"),)
        ordering = ["question", "position"]


class MarkingManager(models.Manager):
    def for_user(self, user, version):  # pylint: disable=too-many-return-statements
        # return self.get_queryset().filter(marking_meta__in=MarkingMeta.objects.for_user(user))
        exams = Exam.objects.for_user(user)
        queryset = self.get_queryset().filter(
            marking_meta__question__exam__in=exams, version=version
        )
        if user.is_superuser:
            return queryset

        # In a first step, we need to find markings which are >=locked/submitted
        # We achieve this by creating individual Q objects for each Action and then concatenating them
        locked_actions = MarkingAction.objects.filter(
            status__gte=MarkingAction.LOCKED_BY_MODERATION
        ).all()
        subm_actions = MarkingAction.objects.filter(
            status__gte=MarkingAction.SUBMITTED_FOR_MODERATION
        ).all()
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

        if user.has_perm("ipho_core.is_marker") or user.has_perm(
            "ipho_core.is_organizer_admin"
        ):
            if version == "O":
                return queryset
            if version == "D":
                # This filters out all >=locked Delegation Markings for exams with Org view after moderation.
                exams_org_view_after_mod = exams.filter(
                    marking_organizer_can_see_delegation_marks__gte=Exam.MARKING_ORGANIZER_VIEW_MODERATION_FINAL
                )
                deleg_marking_view_after_mod_q = (
                    Q(marking_meta__question__exam__in=exams_org_view_after_mod)
                    & locked_action_q
                )
                # This filters out all >=submitted Delegation Markings for exams with Org view after submission.
                exams_org_view_after_subm = exams.filter(
                    marking_organizer_can_see_delegation_marks__gte=Exam.MARKING_ORGANIZER_VIEW_WHEN_SUBMITTED
                )
                deleg_marking_view_after_subm_q = (
                    Q(marking_meta__question__exam__in=exams_org_view_after_subm)
                    & subm_action_q
                )
                return queryset.filter(
                    deleg_marking_view_after_mod_q | deleg_marking_view_after_subm_q
                )

            if version == "F":
                return queryset.filter(locked_action_q)

        if user.has_perm("ipho_core.is_delegation"):
            # A delegation can only view their own markings
            delegs = Delegation.objects.filter(members=user).all()
            queryset = queryset.filter(participant__delegation__in=delegs)

            if version == "O":
                # This filters out all >=submitted Official Markings for exams with Delegation can view after submission.
                exams_deleg_view_after_subm = exams.filter(
                    marking_delegation_can_see_organizer_marks__gte=Exam.MARKING_DELEGATION_VIEW_WHEN_SUBMITTED
                ).all()
                org_marking_view_after_subm_q = (
                    Q(marking_meta__question__exam__in=exams_deleg_view_after_subm)
                    & subm_action_q
                )
                # This filters out all Official markings for exams with delegation can view off marks
                exams_deleg_view_yes = exams.filter(
                    marking_delegation_can_see_organizer_marks__gte=Exam.MARKING_DELEGATION_VIEW_YES
                ).all()
                org_marking_view_always_q = Q(
                    marking_meta__question__exam__in=exams_deleg_view_yes
                )

                return queryset.filter(
                    org_marking_view_after_subm_q | org_marking_view_always_q
                )

            if version == "D":
                return queryset
            if version == "F":
                return queryset.filter(locked_action_q)

        return self.none()

    def editable(self, user, version):
        queryset = self.for_user(user, version)
        if user.is_superuser:
            return queryset

        exams = Exam.objects.for_user(user)

        un_subm_actions = MarkingAction.objects.filter(
            status__lt=MarkingAction.SUBMITTED_FOR_MODERATION
        ).all()

        un_subm_action_q_list = [
            Q(participant__delegation=a.delegation, marking_meta__question=a.question)
            for a in un_subm_actions
        ]
        # Q(pk__in=[]) is an empty Q object which we use as initializer (and default) object in reduce
        un_subm_action_q = reduce(operator.or_, un_subm_action_q_list, Q(pk__in=[]))

        if user.has_perm("ipho_core.is_marker") and version == "O":
            un_final_actions = MarkingAction.objects.filter(
                status__lt=MarkingAction.FINAL
            ).all()
            un_final_action_q_list = [
                Q(
                    participant__delegation=a.delegation,
                    marking_meta__question=a.question,
                )
                for a in un_final_actions
            ]
            un_final_action_q = reduce(
                operator.or_, un_final_action_q_list, Q(pk__in=[])
            )

            # This filters out all <submitted Markings for exams with Org edit if not submitted
            exams_org_edit_before_subm = exams.filter(
                marking_organizer_can_enter__gte=Exam.MARKING_ORGANIZER_CAN_ENTER_IF_NOT_SUBMITTED
            ).all()
            marking_edit_before_subm_q = (
                Q(marking_meta__question__exam__in=exams_org_edit_before_subm)
                & un_subm_action_q
            )

            # This filters out all <final Markings for exams with Org edit if not final
            exams_org_edit_before_final = exams.filter(
                marking_organizer_can_enter__gte=Exam.MARKING_ORGANIZER_CAN_ENTER_IF_NOT_FINAL
            ).all()
            marking_edit_before_final_q = (
                Q(marking_meta__question__exam__in=exams_org_edit_before_final)
                & un_final_action_q
            )
            return queryset.filter(
                marking_edit_before_subm_q | marking_edit_before_final_q
            )

        if user.has_perm("ipho_core.is_delegation") and version == "D":
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
        validators=[],
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
        if not ALLOW_MARKS_NONE and (self.points == "" or self.points is None):
            raise ValidationError(
                {"points": ValidationError("The points cannot be empty.")}
            )
        if self.points == "" or self.points is None:
            return
        try:
            if (
                self.marking_meta.max_points is not None
                and self.points > self.marking_meta.max_points
            ):
                raise ValidationError(
                    {
                        "points": ValidationError(
                            "The number of points cannot exceed the maximum."
                        )
                    }
                )
            if (
                self.marking_meta.min_points is not None
                and self.points < self.marking_meta.min_points
            ):
                raise ValidationError(
                    {
                        "points": ValidationError(
                            "The number of points cannot subceed the minimum."
                        )
                    }
                )
            if not ALLOW_NEGATIVE_MARKS and self.points < 0:
                raise ValidationError(
                    {
                        "points": ValidationError(
                            "The number of points cannot be negative."
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
        unique_together = (("marking_meta", "participant", "version"),)
        ordering = ["marking_meta", "participant", "version"]
