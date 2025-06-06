import json
import uuid

from django.conf import settings

# User should not be imported directly (pylint-django:E5142)
from django.contrib.auth import get_user_model

# other modules expect Group to be here
from django.contrib.auth.models import Group  # pylint: disable=unused-import
from django.db import models

User = get_user_model()

from pywebpush import webpush


class IphoPerm(models.Model):
    class Meta:
        permissions = (
            ("is_delegation", "Is a delegation"),
            ("is_delegation_print", "Is in the print team of a delegation"),
            ("is_marker", "Is a marker"),
            ("can_edit_exam", "Can edit the exam"),
            # "can_manage" is used here (instead of "can_edit") because it only applies to the admin functionalities (i.e. comments/status)
            ("can_manage_feedback", "Can manage feedbacks"),
            ("can_edit_poll", "Can edit polls"),
            ("can_vote", "Can vote"),
            (
                "can_see_boardmeeting",
                "Can see the exam, feedbacks, and votes when they are available to delegations",
            ),
            ("is_organizer_admin", "Is an organizer admin"),
            ("can_impersonate", "Can impersonate delegations"),
            ("can_access_control", "Can access the control app"),
            ("can_print_boardmeeting_site", "Can print at the boardmeeting site"),
            ("can_print_exam_site", "Can print at the exam site"),
            ("is_printstaff", "Is a print staff"),
        )


class DelegationManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Delegation(models.Model):
    objects = DelegationManager()

    max_length = 10
    if len(settings.OFFICIAL_DELEGATION) > max_length:
        raise RuntimeError(
            f"the name '{settings.OFFICIAL_DELEGATION}' is longer than the database field max_length='{max_length}'"
        )

    name = models.CharField(unique=True, max_length=max_length)
    country = models.CharField(unique=True, max_length=100)
    members = models.ManyToManyField(User, blank=True)
    auto_translate_char_count = models.IntegerField(default=0)

    class Meta:
        ordering = ["name"]

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return f"{self.country} ({self.name})"

    def get_participants(self, exam):
        return self.participant_set.filter(exam=exam)


class StudentManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class Student(models.Model):
    objects = StudentManager()

    code = models.CharField(max_length=10, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    delegation = models.ForeignKey(Delegation, on_delete=models.CASCADE)

    class Meta:
        ordering = ["code"]

    def natural_key(self):
        return (self.code,)

    def __str__(self):
        return f"{self.code}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class PushSubscriptionManager(models.Manager):
    def get_by_data(self, data):
        subs_list = super().get_queryset().all()

        def compare_json(data1, data2):
            return json.loads(data1) == json.loads(data2)

        pk_list = []
        for subs in subs_list:
            if compare_json(subs.data, data):
                pk_list.append(subs.pk)
        qset = super().get_queryset().filter(pk__in=pk_list)
        return qset


class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    objects = PushSubscriptionManager()

    def __str__(self):
        return f"Push data of {self.user}"

    def send(self, data):
        sub_data = json.loads(self.data)
        claims = {"sub": "mailto:noreply@oly-exams.org"}
        # import cProfile as profile
        # profile.runctx('webpush(sub_data,json.dumps(data),vapid_claims=claims,vapid_private_key=settings.PUSH_PRIVATE_KEY,)', globals(), locals(),"webpush.prof")
        res = webpush(
            sub_data,
            json.dumps(data),
            vapid_claims=claims,
            vapid_private_key=settings.PUSH_PRIVATE_KEY,
        )
        return res


class AccountRequest(models.Model):
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.email} ({self.user}) - {self.timestamp}"


class RandomDrawLog(models.Model):
    delegation = models.ForeignKey(Delegation, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=200,
        default="pending",
        choices=(
            ("pending", "Pending"),
            ("received", "Received"),
            ("failed", "Failed"),
        ),
    )
    tag = models.CharField(max_length=200, default="")

    def __str__(self):
        return f"{self.delegation} - {self.status}"
