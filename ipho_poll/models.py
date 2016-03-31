from django.utils import timezone
from django.db import models
from ipho_core.models import Delegation

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

class Question(models.Model):
    question_text = models.TextField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('end date', blank=True, null=True)
    objects = QuestionManager()
    def __str__(self):
        return self.question_text
    def is_closed(self):
        if self.end_date:
            return self.end_date <= timezone.now()
        else:
            return False

class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    def __str__(self):
        return self.choice_text

class Vote(models.Model):
    question = models.ForeignKey(Question, default="")
    choice = models.ForeignKey(Choice)
    delegation = models.ForeignKey(Delegation)
