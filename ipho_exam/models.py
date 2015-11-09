from django.db import models
from ipho_core.models import Delegation, Student
from django.shortcuts import get_object_or_404

class LanguageManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
class Language(models.Model):
    objects = LanguageManager()

    POLYGLOSSIA_CHOICES = (('albanian', 'Albanian'), ('amharic', 'Amharic'), ('arabic', 'Arabic'), ('armenian', 'Armenian'), ('asturian', 'Asturian'), ('bahasai', 'Bahasai'), ('bahasam', 'Bahasam'), ('basque', 'Basque'), ('bengali', 'Bengali'), ('brazilian', 'Brazilian'), ('breton', 'Breton'), ('bulgarian', 'Bulgarian'), ('catalan', 'Catalan'), ('coptic', 'Coptic'), ('croatian', 'Croatian'), ('czech', 'Czech'), ('danish', 'Danish'), ('divehi', 'Divehi'), ('dutch', 'Dutch'), ('english', 'English'), ('esperanto', 'Esperanto'), ('estonian', 'Estonian'), ('farsi', 'Farsi'), ('finnish', 'Finnish'), ('french', 'French'), ('friulan', 'Friulan'), ('galician', 'Galician'), ('german', 'German'), ('greek', 'Greek'), ('hebrew', 'Hebrew'), ('hindi', 'Hindi'), ('icelandic', 'Icelandic'), ('interlingua', 'Interlingua'), ('irish', 'Irish'), ('italian', 'Italian'), ('kannada', 'Kannada'), ('lao', 'Lao'), ('latin', 'Latin'), ('latvian', 'Latvian'), ('lithuanian', 'Lithuanian'), ('lsorbian', 'Lsorbian'), ('magyar', 'Magyar'), ('malayalam', 'Malayalam'), ('marathi', 'Marathi'), ('nko', 'Nko'), ('norsk', 'Norsk'), ('nynorsk', 'Nynorsk'), ('occitan', 'Occitan'), ('piedmontese', 'Piedmontese'), ('polish', 'Polish'), ('portuges', 'Portuges'), ('romanian', 'Romanian'), ('romansh', 'Romansh'), ('russian', 'Russian'), ('samin', 'Samin'), ('sanskrit', 'Sanskrit'), ('scottish', 'Scottish'), ('serbian', 'Serbian'), ('slovak', 'Slovak'), ('slovenian', 'Slovenian'), ('spanish', 'Spanish'), ('swedish', 'Swedish'), ('syriac', 'Syriac'), ('tamil', 'Tamil'), ('telugu', 'Telugu'), ('thai', 'Thai'), ('tibetan', 'Tibetan'), ('turkish', 'Turkish'), ('turkmen', 'Turkmen'), ('ukrainian', 'Ukrainian'), ('urdu', 'Urdu'), ('usorbian', 'Usorbian'), ('vietnamese', 'Vietnamese'), ('welsh', 'Welsh'))

    name = models.CharField(max_length=100, unique=True)
    delegation  = models.ForeignKey(Delegation, blank=True, null=True)
    hidden      = models.BooleanField(default=False)
    versioned   = models.BooleanField(default=False)
    polyglossia = models.CharField(max_length=100, default='english', choices=POLYGLOSSIA_CHOICES)
    extraheader = models.TextField(blank=True)

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
    feedback_active = models.BooleanField(default=False, help_text='Are feedbacks allowed?')

    def __unicode__(self):
        return u'%s' % (self.name)


class Question(models.Model):
    name = models.CharField(max_length=100)
    exam = models.ForeignKey(Exam)
    position = models.PositiveSmallIntegerField(help_text='Sorting index inside one exam')

    class Meta:
        ordering = ['position']

    def exam_name(self):
        return self.exam.name

    def __unicode__(self):
        return u'{} [#{} in {}]'.format(self.name, self.position, self.exam.name)


class VersionNode(models.Model):
    STATUS_CHOICES = (
        ('P', 'Proposal'),
        ('C', 'Confirmed'),
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
        ('O', 'In progress'),
        ('L', 'Locked'),
        ('S', 'Submitted'),
    )

    text      = models.TextField(blank=True)
    question  = models.ForeignKey(Question)
    language  = models.ForeignKey(Language)
    status    = models.CharField(max_length=1, choices=STATUS_CHOICES, default='O')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('question', 'language'),)

    def question_name(self):
        return self.question.name

    def __unicode__(self):
        return u'node: {} [{}, {}] - {}'.format(self.question.name, self.language, self.timestamp, self.status)


class Figure(models.Model):
    name    = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    params  = models.TextField(blank=True)

    def params_as_list(self):
        return list([si.trim() for si in self.params.split(',')])

    def __unicode__(self):
        return u'%s' % (self.name)

    @staticmethod
    def get_fig_query(fig_id, query):
        fig = get_object_or_404(Figure, pk=fig_id)
        placeholders = fig.params.split(',')
        fig_svg = fig.content
        for pl in placeholders:
            if pl in query:
                repl = query[pl]
                if type(repl) != unicode:
                    repl = repl.decode('utf-8')
                fig_svg = fig_svg.replace(u'%{}%'.format(pl), repl)
        return fig_svg


class Feedback(models.Model):
    STATUS_CHOICES = (
        ('O', 'In progress'),
        ('A', 'Accepted'),
        ('R', 'Rejected'),
    )

    delegation = models.ForeignKey(Delegation)
    question  = models.ForeignKey(Question)
    comment   = models.TextField(blank=True)
    status    = models.CharField(max_length=1, choices=STATUS_CHOICES, default='O')
    timestamp = models.DateTimeField(auto_now=True)

class ExamDelegationSubmission(models.Model):
    STATUS_CHOICES = (
        ('O', 'In progress'),
        ('S', 'Translations submitted'),
        ('A', 'Translations assigned'),
    )
    exam       = models.ForeignKey(Exam)
    delegation = models.ForeignKey(Delegation)
    status     = models.CharField(max_length=1, choices=STATUS_CHOICES, default='O')
    timestamp  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('exam', 'delegation'),)

class StudentSubmission(models.Model):
    student  = models.ForeignKey(Student)
    exam     = models.ForeignKey(Exam)
    language = models.ForeignKey(Language)
    ## TODO: do we need a status? (in progress, submitted, printed)

    class Meta:
        unique_together = (('student', 'exam', 'language'),)
