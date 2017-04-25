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

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
import uuid

class IphoPerm(models.Model):
    pass
    class Meta:
            permissions = (
                ('is_delegation', 'Is a delegation'),
                ('is_marker', 'Is a marker'),
                ('can_vote', 'Can vote'),
                ('is_staff', 'Is an organizer'),
                ('print_technopark', 'Can print in Technopark'),
                ('print_irchel', 'Can print in Irchel'),
                ('is_printstaff', 'Is a print staff'),
            )

class AutoLoginManager(models.Manager):
    def get_by_natural_key(self, username):
        return self.get(user=User.objects.get_by_natural_key(username))
class AutoLogin(models.Model):
    objects = AutoLoginManager()

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)

    def __unicode__(self):
        return unicode(self.token)

    def natural_key(self):
        return self.user.natural_key()

class DelegationManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
class Delegation(models.Model):
    objects = DelegationManager()

    name    = models.CharField(unique=True,max_length=max(3, len(settings.OFFICIAL_DELEGATION)))
    country = models.CharField(unique=True,max_length=100)
    members = models.ManyToManyField(User, blank=True)

    class Meta:
        ordering = ['name']

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

    class Meta:
        ordering = ['code']

    def natural_key(self):
        return (self.code,)

    def __unicode__(self):
        return u'{}'.format(self.code)
