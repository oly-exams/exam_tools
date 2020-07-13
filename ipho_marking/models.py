# Exam Tools
#
# Copyright (C) 2014 - 2019 Oly Exams Team
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
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.encoding import python_2_unicode_compatible

from ipho_core.models import Student, Delegation
from ipho_exam.models import Exam, Question
from ipho_exam.exceptions import IphoExamForbidden
from collections import OrderedDict



class MarkingActionManager(models.Manager):
    def get_by_natural_key(self, question_id, delegation_name, action):
        return self.get(question__id=exam_name, delegation__name=delegation_name, action=action)


class MarkingAction(models.Model):
    objects = MarkingActionManager()

    OPEN = 0
    SUBMITTED = 1
    LOCKED = 2
    FINAL = 3
    STATUS_CHOICES = (
        (OPEN, 'In progress'),
        (SUBMITTED, 'Submitted'),
        (LOCKED, 'Locked'),
        (FINAL, 'Final'),
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    delegation = models.ForeignKey(Delegation, related_name='marking_status', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta(object):
        unique_together = (('question', 'delegation'),)
        index_together = unique_together

    def natural_key(self):
        return self.question.natural_key() + self.delegation.natural_key()

    natural_key.dependencies = ['ipho_exam.question', 'ipho_core.delegation']

    def in_progress(self):
        return self.status == MarkingAction.OPEN

    @staticmethod
    def exam_in_progress(exam, delegation):
        marks_open = MarkingAction.objects.filter(
            question__exam=exam, delegation=delegation, status=MarkingAction.OPEN
        ).exists()
        return marks_open


@receiver(post_save, sender=Question, dispatch_uid='create_marking_actions_on_question_creation')
def create_actions_on_exam_creation(instance, created, raw, **kwargs):
    # Ignore fixtures and saves for existing courses.
    if not created or raw or instance.type != Question.ANSWER:
        return
    for delegation in Delegation.objects.all():
        marking_action, _ = MarkingAction.objects.get_or_create(question=instance, delegation=delegation)


@receiver(post_save, sender=Delegation, dispatch_uid='create_marking_actions_on_delegation_creation')
def create_actions_on_delegation_creation(instance, created, raw, **kwargs):
    # Ignore fixtures and saves for existing courses.
    if not created or raw:
        return
    for question in Question.objects.filter(type=Question.ANSWER).all():
        marking_action, _ = MarkingAction.objects.get_or_create(question=question, delegation=instance)



@python_2_unicode_compatible
class MarkingMeta(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    max_points = models.DecimalField(max_digits=8, decimal_places=2)
    position = models.PositiveSmallIntegerField(default=10, help_text='Sorting index inside one question')

    def __str__(self):
        return u'{} [{}] {} points'.format(self.name, self.question.name, self.max_points)

    class Meta(object):
        ordering = ['position']
        unique_together = index_together = (('question', 'name'), )


@python_2_unicode_compatible
class Marking(models.Model):
    marking_meta = models.ForeignKey(MarkingMeta, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    points = models.DecimalField(
        null=True, blank=True, max_digits=8, decimal_places=2, validators=[MinValueValidator(0.)]
    )
    comment = models.TextField(null=True, blank=True)
    MARKING_VERSIONS = OrderedDict([
        ('O', 'Organizers'),
        ('D', 'Delegation'),
        ('F', 'Final'),
    ])
    version = models.CharField(max_length=1, choices=list(MARKING_VERSIONS.items()))

    def clean(self):
        try:
            if self.points > self.marking_meta.max_points:
                raise ValidationError('The number of points cannot exceed the maximum.')
        except TypeError:
            raise ValidationError('The number of points must be a number.')

    def exam_question(self):
        return self.marking_meta.question

    def __str__(self):
        return u'{} [{} / {}]'.format(self.marking_meta.name, self.points, self.marking_meta.max_points)

    class Meta(object):
        unique_together = (('marking_meta', 'student', 'version'), )
