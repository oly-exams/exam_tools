from django.db import models


from ipho_core.models import Student

from ipho_exam.models import Exam, Question

class MarkingMeta(models.Model):
    question = models.ForeignKey(Question)
    name = models.CharField(max_length=2)
    max_points = models.FloatField()
    position = models.PositiveSmallIntegerField(help_text='Sorting index inside one question')



class Marking(models.Model):
    marking_meta = models.ForeignKey(MarkingMeta)
    student = models.ForeignKey(Student)
    points = models.FloatField()
    comment = models.TextField()
    MARKING_VERSIONS = (
        ('O', 'Organizers'),
        ('D', 'Delegation'),
        ('F', 'Final'),
    )
    version = models.CharField(max_length=1, choices=MARKING_VERSIONS)

    def __unicode__(self):
        return u'{} [{} / {}]'.format(self.question_points.name, self.points, self.marking_meta.max_points)
