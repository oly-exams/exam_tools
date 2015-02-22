from django.db import models
from django.contrib.auth.models import User, Group



class Delegation(models.Model):
    name    = models.CharField(unique=True,max_length=3)
    country = models.CharField(unique=True,max_length=100)
    members = models.ManyToManyField(User)

    def __unicode__(self):
        return u'{} ({})'.format(self.country, self.name)

class Student(models.Model):
    code           = models.CharField(max_length=10, unique=True)
    firstname      = models.CharField(max_length=200)
    lastname       = models.CharField(max_length=200)
    delegation     = models.ForeignKey(Delegation)
    # exam_languages = models.ManyToManyField(Language)

    def __unicode__(self):
        return '{} {}'.format(self.firstname, self.lastname)

