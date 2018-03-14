# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
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

from builtins import chr
from builtins import object
from django.utils import timezone
from django.db import models
from ipho_core.models import Delegation
from django.contrib.auth.models import User
from django.db.models import Q, Count
from itertools import chain

from ipho_exam.models import Feedback


class QuestionManager(models.Manager):
    def is_draft(self):
        queryset = Question.objects.filter(end_date__isnull=True)
        return queryset

    def is_open(self):
        queryset = Question.objects.filter(end_date__gt=timezone.now)
        return queryset

    def is_closed(self):
        queryset = Question.objects.filter(end_date__lte=timezone.now)
        return queryset

    def not_voted_upon_by(self, user):
        user_tot_votes = user.votingright_set.all().count()
        qNotFull = Question.objects.is_open().filter(vote__voting_right__user=user
                                                     ).annotate(user_votes=Count('vote')
                                                                ).filter(user_votes__lt=user_tot_votes)
        qNoVotes = Question.objects.is_open().exclude(vote__voting_right__user=user)
        return list(chain(qNotFull, qNoVotes))


class Question(models.Model):
    class VOTE_RESULT_META(object):
        OPEN = 0
        REJECTED = 1
        ACCEPTED = 2
        choices = (
            (OPEN, 'In progress'),
            (REJECTED, 'Rejected'),
            (ACCEPTED, 'Accepted'),
        )

    class IMPLEMENTATION_META(object):
        NOT_IMPL = 0
        IMPL = 1
        choices = (
            (NOT_IMPL, 'Not implemented'),
            (IMPL, 'Implemented'),
        )

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('end date', blank=True, null=True)
    vote_result = models.PositiveSmallIntegerField(choices=VOTE_RESULT_META.choices, default=VOTE_RESULT_META.OPEN)
    implementation = models.PositiveSmallIntegerField(
        choices=IMPLEMENTATION_META.choices, default=IMPLEMENTATION_META.NOT_IMPL
    )
    feedbacks = models.ManyToManyField(Feedback, blank=True, related_name='vote')
    objects = QuestionManager()

    def __str__(self):
        return self.title

    def is_draft(self):
        if not self.end_date:
            return True
        else:
            return False

    def is_open(self):
        if not self.is_draft() and not self.is_closed():
            return True
        else:
            return False

    def is_closed(self):
        if self.end_date:
            return self.end_date <= timezone.now()
        else:
            return False

    def choice_dict(self):
        choice_set = self.choice_set.all()
        choice_dict = {}
        for i, choice in enumerate(choice_set):
            choice_dict[choice] = chr(ord('A') + i)
        return choice_dict


class Choice(models.Model):
    question = models.ForeignKey(Question)
    label = models.CharField(max_length=3, blank=True, null=True)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return '{}. {}'.format(self.label, self.choice_text)

    def calculateVotes(self):
        return Vote.objects.filter(choice=self).count()

    votes = property(calculateVotes)

    class Meta(object):
        ordering = ['label']


class VotingRight(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Vote(models.Model):
    question = models.ForeignKey(Question)
    choice = models.ForeignKey(Choice)
    voting_right = models.ForeignKey(VotingRight)

    def __str__(self):
        return self.choice.__str__()

    class Meta(object):
        unique_together = (('question', 'voting_right'))
