from django.utils import timezone
from django.db import models
from ipho_core.models import Delegation

class Question(models.Model):
    question_text = models.TextField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('end date', blank=True, null=True, input_formats=['%m/%d/%Y %H:%M:%S',])
    STATUS_CHOICES = (
        (0, "draft"),
        (1, "open"),
        (2, "closed"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    def __str__(self):
        return self.choice_text

class Vote(models.Model):
    choice = models.ForeignKey(Choice)
    delegation = models.ForeignKey(Delegation)
