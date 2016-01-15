import datetime

from django.db import models
from ipho_core.models import Delegation

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    STATUS_CHOICES = (
        (0, "draft"),
        (1, "live"),
        (2, "closed"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0) 
    def __str__(self):
        return "Question Text: " + self.question_text + " / Status: " + self.status 

class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text

class Vote(models.Model):
    choice = models.ForeignKey(Choice)
    delegation = models.ForeignKey(Delegation)    
