# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from builtins import object
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

    class Meta(object):
        ordering = ['position']
        unique_together = index_together = (('question', 'name'), )


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
    version = models.CharField(max_length=1, choices=list(MARKING_VERSIONS.items()))

    def exam_question(self):
        return self.marking_meta.question

    def __unicode__(self):
        return u'{} [{} / {}]'.format(self.marking_meta.name, self.points, self.marking_meta.max_points)

    class Meta(object):
        unique_together = (('marking_meta', 'student', 'version'), )
