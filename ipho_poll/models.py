from django.utils import timezone
from django.db import models
from ipho_core.models import Delegation
from django.contrib.auth.models import User
from django.db.models import Q, Count
from itertools import chain


class QuestionManager(models.Manager):
    def is_draft(self):
        queryset = Question.objects.filter(end_date__isnull = True)
        return queryset
    def is_open(self):
        queryset = Question.objects.filter(end_date__gt = timezone.now)
        return queryset
    def is_closed(self):
        queryset = Question.objects.filter(end_date__lte = timezone.now)
        return queryset
    def not_voted_upon_by(self, user):
        user_tot_votes = user.votingright_set.all().count()
        qNotFull = Question.objects.is_open().filter(vote__voting_right__user=user).annotate(user_votes=Count('vote')).filter(user_votes__lt=user_tot_votes)
        qNoVotes = Question.objects.is_open().exclude(vote__voting_right__user=user)
        return list(chain(qNotFull, qNoVotes))



class Question(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('end date', blank=True, null=True)
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
        for i,choice in enumerate(choice_set)   :
            choice_dict[choice] = chr(ord('A')+i)
        return choice_dict




class Choice(models.Model):
    question = models.ForeignKey(Question)
    label = models.CharField(max_length=3, blank=True, null=True)
    choice_text = models.CharField(max_length=200)
    def __str__(self):
        return '{}. {}'.format( self.label,self.choice_text)

    def calculateVotes(self):
        return Vote.objects.filter(choice = self).count()
    votes = property(calculateVotes)

class VotingRight(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Vote(models.Model):
    question = models.ForeignKey(Question) #Should be removed
    choice = models.ForeignKey(Choice)
    voting_right = models.ForeignKey(VotingRight)

    def __str__(self):
        return self.choice.__str__()
