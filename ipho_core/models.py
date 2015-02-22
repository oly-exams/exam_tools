from django.db import models
from django.contrib.auth.models import User, Group



class Delegation(models.Model):
    name    = models.CharField(unique=True,max_length=3)
    country = models.CharField(unique=True,max_length=100)
    members = models.ManyToManyField(User, blank=True)

    def __unicode__(self):
        return u'{} ({})'.format(self.country, self.name)

class Student(models.Model):
    code           = models.CharField(max_length=10, unique=True)
    first_name     = models.CharField(max_length=200)
    last_name      = models.CharField(max_length=200)
    delegation     = models.ForeignKey(Delegation)
    # exam_languages = models.ManyToManyField(Language)

    def __unicode__(self):
        return u'{} {}'.format(self.first_name, self.last_name)

