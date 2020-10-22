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

from itertools import chain

# User should not be imported directly (pylint-django:E5142)
from django.contrib.auth import get_user_model

User = get_user_model()
from django.utils import timezone
from django.db import models
from django.db.models import Count
from ipho_exam.models import Feedback


class QuestionManager(models.Manager):
    def is_draft(self):  # pylint: disable=no-self-use
        queryset = Question.objects.filter(end_date__isnull=True)
        return queryset

    def is_open(self):  # pylint: disable=no-self-use
        queryset = Question.objects.filter(end_date__gt=timezone.now())
        return queryset

    def is_closed(self):  # pylint: disable=no-self-use
        queryset = Question.objects.filter(end_date__lte=timezone.now())
        return queryset

    def not_voted_upon_by(self, user):  # pylint: disable=no-self-use
        user_tot_votes = user.votingright_set.all().count()
        q_not_full = (
            Question.objects.is_open()
            .filter(vote__voting_right__user=user)
            .annotate(user_votes=Count("vote"))
            .filter(user_votes__lt=user_tot_votes)
        )
        q_no_votes = Question.objects.is_open().exclude(vote__voting_right__user=user)
        return list(chain(q_not_full, q_no_votes))


class Question(models.Model):
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
    pub_date = models.DateTimeField("date published", default=timezone.now)
    end_date = models.DateTimeField("end date", blank=True, null=True)
    vote_result = models.PositiveSmallIntegerField(
        choices=VoteResultMeta.choices, default=VoteResultMeta.OPEN
    )
    implementation = models.PositiveSmallIntegerField(
        choices=ImplementationMeta.choices, default=ImplementationMeta.NOT_IMPL
    )
    feedbacks = models.ManyToManyField(Feedback, blank=True, related_name="vote")
    objects = QuestionManager()

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
        choice_set = self.choice_set.all()
        choice_dict = {}
        for i, choice in enumerate(choice_set):
            choice_dict[choice] = chr(ord("A") + i)
        return choice_dict


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    label = models.CharField(max_length=3, blank=True, null=True)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        if self.label == "zzz" and "abstain" in self.choice_text.lower():
            return self.choice_text
        return f"{self.label}. {self.choice_text}"

    def calculate_votes(self):
        return Vote.objects.filter(choice=self).count()

    votes = property(calculate_votes)

    class Meta:
        ordering = ["label"]


class VotingRight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.user})"


class Vote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voting_right = models.ForeignKey(VotingRight, on_delete=models.CASCADE)

    def __str__(self):
        return self.choice.__str__()

    class Meta:
        unique_together = ("question", "voting_right")
