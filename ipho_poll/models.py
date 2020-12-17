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

# User should not be imported directly (pylint-django:E5142)
from django.contrib.auth import get_user_model

User = get_user_model()
from django.utils import timezone
from django.db import models
from django.db.models import Count, Q
from django.core.exceptions import ValidationError
from ipho_exam.models import Feedback


class VotingRoomQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.filter(visibility__gte=VotingRoom.VISIBLE_2ND_LVL_SUPPORT_ONLY)

        if user.has_perm("ipho_core.can_edit_poll"):
            return self.filter(
                visibility__gte=VotingRoom.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT
            )
        if user.votingright_set.exists():
            return self.filter(
                visibility__gte=VotingRoom.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT_AND_BOARDMEETING
            )
        return self.none()


class VotingRoom(models.Model):
    # pylint: disable=invalid-name
    name = models.CharField(max_length=100, unique=True)

    # Note that IntegerFields enable us to filter using order relations.
    # We mostly use >=/__gte to filter the hierarchical flags
    # e.g. visibility__gte=Orga+2nd_level shows the exam when the visibility
    # is set to orgas+2nd_level or orgas+2nd_level+boardmeeting

    VISIBLE_2ND_LVL_SUPPORT_ONLY = -1
    VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT = 0
    VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT_AND_BOARDMEETING = 1
    VISIBILITY_CHOICES = (
        (VISIBLE_2ND_LVL_SUPPORT_ONLY, "2nd level support only"),
        (VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT, "Organizer + 2nd level support"),
        (
            VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT_AND_BOARDMEETING,
            "Boardmeeting + Organizer + 2nd level support",
        ),
    )

    visibility = models.IntegerField(
        default=1,
        choices=VISIBILITY_CHOICES,
        help_text="Sets the visibility of the voting room for organizers and delegations.",
        verbose_name="Voting Room Visibility",
    )

    objects = VotingRoomQuerySet.as_manager()

    def __str__(self):
        return self.name


class VotingQuerySet(models.QuerySet):
    def is_draft(self):
        return self.filter(end_date__isnull=True)

    def is_open(self):
        return self.filter(end_date__gt=timezone.now())

    def is_closed(self):
        return self.filter(end_date__lte=timezone.now())

    def not_voted_upon_by(self, user):
        # pylint: disable=invalid-name
        user_tot_votes = user.votingright_set.all().count()
        not_full = (
            self.filter(castedvote__voting_right__user=user)
            .annotate(user_votes=Count("castedvote"))
            .filter(user_votes__lt=user_tot_votes)
            .values_list("pk", flat=True)
        )
        Q_not_full = Q(pk__in=not_full)
        Q_no_votes = ~Q(castedvote__voting_right__user=user)
        not_voted = self.filter(Q_not_full | Q_no_votes)
        return not_voted


class Voting(models.Model):
    class VoteResultMeta:
        OPEN = 0
        REJECTED = 1
        ACCEPTED = 2
        choices = (
            (OPEN, "In progress"),
            (REJECTED, "Rejected"),
            (ACCEPTED, "Accepted"),
        )

    class ImplementationMeta:
        NOT_IMPL = 0
        IMPL = 1
        choices = (
            (NOT_IMPL, "Not implemented"),
            (IMPL, "Implemented"),
        )

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    voting_room = models.ForeignKey(
        VotingRoom, null=True, blank=True, on_delete=models.SET_NULL
    )
    pub_date = models.DateTimeField("date published", default=timezone.now)
    end_date = models.DateTimeField("end date", blank=True, null=True)
    vote_result = models.PositiveSmallIntegerField(
        choices=VoteResultMeta.choices, default=VoteResultMeta.OPEN
    )
    implementation = models.PositiveSmallIntegerField(
        choices=ImplementationMeta.choices, default=ImplementationMeta.NOT_IMPL
    )
    feedbacks = models.ManyToManyField(Feedback, blank=True, related_name="vote")
    objects = VotingQuerySet.as_manager()

    def __str__(self):
        return self.title

    def is_draft(self):
        return not self.end_date

    def is_open(self):
        return not self.is_draft() and not self.is_closed()

    def is_closed(self):
        if self.end_date:
            return self.end_date <= timezone.now()

        return False

    def choice_dict(self):
        votingchoice_set = self.votingchoice_set.all()
        choice_dict = {}
        for i, choice in enumerate(votingchoice_set):
            choice_dict[choice] = chr(ord("A") + i)
        return choice_dict


class VotingChoice(models.Model):
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE)
    label = models.CharField(max_length=3, blank=True, null=True)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        if self.label == "zzz" and "abstain" in self.choice_text.lower():
            return self.choice_text
        return f"{self.label}. {self.choice_text}"

    def calculate_votes(self):
        return CastedVote.objects.filter(choice=self).count()

    votes = property(calculate_votes)

    class Meta:
        ordering = ["label"]


class VotingRight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.user})"


class CastedVote(models.Model):
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE)
    choice = models.ForeignKey(VotingChoice, on_delete=models.CASCADE)
    voting_right = models.ForeignKey(VotingRight, on_delete=models.CASCADE)

    def __str__(self):
        return self.choice.__str__()

    def clean(self):
        super().clean()
        if timezone.now() > self.voting.end_date:
            raise ValidationError(
                "Voting is already closed, cannot save this vote. Please reload the page."
            )

    class Meta:
        unique_together = ("voting", "voting_right")
