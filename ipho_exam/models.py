from django.db import models
from ipho_core.models import Delegation, Student


class LanguageManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
class Language(models.Model):
    objects = LanguageManager()
    
    name = models.CharField(max_length=100, unique=True)
    delegation = models.ManyToManyField(Delegation, blank=True) # TODO: make a ForeignKey
    hidden     = models.BooleanField(default=False)
    versioned  = models.BooleanField(default=False)
    
    def natural_key(self):
        return (self.name,)
    
    def __unicode__(self):
        return u'%s' % (self.name)

    def check_permission(self, user):
        if user.is_superuser:
            return True
        else:
            return self.delegation.filter(members=user).exists()


class Exam(models.Model):
    name   = models.CharField(max_length=100)
    active = models.BooleanField(default=True,  help_text='Only active exams are editable.')
    hidden = models.BooleanField(default=False, help_text='Is the exam hidden for the delegations?')
    
    def __unicode__(self):
        return u'%s' % (self.name)


class Question(models.Model):
    name = models.CharField(max_length=100)
    exam = models.ForeignKey(Exam)
    position = models.PositiveSmallIntegerField(help_text='Sortign index inside one exam')
    
    class Meta:
        ordering = ['position']
    
    def exam_name(self):
        return self.exam.name
    
    def __unicode__(self):
        return u'{} [#{} in {}]'.format(self.name, self.position, self.exam.name)


class VersionNode(models.Model):
    STATUS_CHOICES = (
        ('P', 'proposal'),
        ('C', 'confirmed'),
    )
    
    text      = models.TextField()
    question  = models.ForeignKey(Question)
    version   = models.IntegerField()
    language  = models.ForeignKey(Language)
    status    = models.CharField(max_length=1, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = (('question', 'language', 'version'),)
    
    def question_name(self):
        return self.question.name
    
    def __unicode__(self):
        return u'vnode: {} [{}, v{}, {}] - {}'.format(self.question.name, self.language, self.version, self.timestamp, self.status)


class TranslationNode(models.Model):
    STATUS_CHOICES = (
        ('O', 'open'),
        ('L', 'locked'),
        ('S', 'submitted'),
    )
    
    text      = models.TextField()
    question  = models.ForeignKey(Question)
    language  = models.ForeignKey(Language)
    status    = models.CharField(max_length=1, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = (('question', 'language'),)
    
    def question_name(self):
        return self.question.name
    
    def __unicode__(self):
        return u'node: {} [{}, {}] - {}'.format(self.question.name, self.language, self.timestamp, self.status)

