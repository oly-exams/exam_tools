from django.db import models

from ipho_core.models import Student
from ipho_exam.models import Exam, Question
from collections import OrderedDict

class MarkingMeta(models.Model):
    question = models.ForeignKey(Question)
    name = models.CharField(max_length=10)
    max_points = models.FloatField()
    position = models.PositiveSmallIntegerField(default=10, help_text='Sorting index inside one question')

    def __unicode__(self):
        return u'{} [{}] {} points'.format(self.name, self.question.name, self.max_points)

    class Meta:
        ordering = ['position']
        unique_together = index_together = (('question', 'name'),)

class Marking(models.Model):
    marking_meta = models.ForeignKey(MarkingMeta)
    student = models.ForeignKey(Student)
    points = models.FloatField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    MARKING_VERSIONS = OrderedDict([
        ('O', 'Organizers'),
        ('D', 'Delegation'),
        ('F', 'Final'),
    ])
    version = models.CharField(max_length=1, choices=MARKING_VERSIONS.iteritems())

    def exam_question(self):
        return self.marking_meta.question

    def __unicode__(self):
        return u'{} [{} / {}]'.format(self.marking_meta.name, self.points, self.marking_meta.max_points)

    class Meta:
        unique_together = (('marking_meta', 'student', 'version'),)
