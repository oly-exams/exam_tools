from django.db import models
from django.contrib.auth.models import User, Group

class DelegationManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
class Delegation(models.Model):
    objects = DelegationManager()
    
    name    = models.CharField(unique=True,max_length=3)
    country = models.CharField(unique=True,max_length=100)
    members = models.ManyToManyField(User, blank=True)
    
    def natural_key(self):
        return (self.name,)
    
    def __unicode__(self):
        return u'{} ({})'.format(self.country, self.name)

class StudentManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)
class Student(models.Model):
    objects = StudentManager()
    
    code           = models.CharField(max_length=10, unique=True)
    first_name     = models.CharField(max_length=200)
    last_name      = models.CharField(max_length=200)
    delegation     = models.ForeignKey(Delegation)
    # exam_languages = models.ManyToManyField(Language)
    
    def natural_key(self):
        return (self.code,)
    
    def __unicode__(self):
        return u'{} {}'.format(self.first_name, self.last_name)

