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

from __future__ import unicode_literals

from builtins import object
from builtins import str

from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User, Group
import uuid
import json
from pywebpush import webpush, WebPushException



class IphoPerm(models.Model):
    pass

    class Meta(object):
        permissions = (
            ('is_delegation', 'Is a delegation'),
            ('is_marker', 'Is a marker'),
            ('can_vote', 'Can vote'),
            ('is_staff', 'Is an organizer'),
            ('can_impersonate', 'Can impersonate delegations'),
            ('print_technopark', 'Can print in Technopark'),
            ('print_irchel', 'Can print in Irchel'),
            ('is_printstaff', 'Is a print staff'),
        )


class AutoLoginManager(models.Manager):
    def get_by_natural_key(self, username):
        return self.get(user=User.objects.get_by_natural_key(username))


@python_2_unicode_compatible
class AutoLogin(models.Model):
    objects = AutoLoginManager()

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.token)

    def natural_key(self):
        return self.user.natural_key()


class DelegationManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


@python_2_unicode_compatible
class Delegation(models.Model):
    objects = DelegationManager()

    name = models.CharField(unique=True, max_length=max(3, len(settings.OFFICIAL_DELEGATION)))
    country = models.CharField(unique=True, max_length=100)
    members = models.ManyToManyField(User, blank=True)
    auto_translate_char_count = models.IntegerField(default=0)

    class Meta(object):
        ordering = ['name']

    def natural_key(self):
        return (self.name, )

    def __str__(self):
        return u'{} ({})'.format(self.country, self.name)


class StudentManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


@python_2_unicode_compatible
class Student(models.Model):
    objects = StudentManager()

    code = models.CharField(max_length=10, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    delegation = models.ForeignKey(Delegation, on_delete=models.CASCADE)

    # exam_languages = models.ManyToManyField(Language)

    class Meta(object):
        ordering = ['code']

    def natural_key(self):
        return (self.code, )

    def __str__(self):
        return u'{}'.format(self.code)

class PushSubscriptionManager(models.Manager):
    def get_by_data(self, data):
        subs_list = super(PushSubscriptionManager, self).get_queryset().all()
        def compare_json(d1, d2):
            return json.loads(d1) == json.loads(d2)
        pk_list = []
        for subs in subs_list:
            if compare_json(subs.data, data):
                pk_list.append(subs.pk)
        qset = super(PushSubscriptionManager, self).get_queryset().filter(pk__in=pk_list)
        return qset

class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    objects = PushSubscriptionManager()
    def __str__(self):
        return u'Push data of {}'.format(self.user)

    def send(self, data):
        sub_data = json.loads(self.data)
        claims = {'sub':'mailto:noreply@oly-exams.org'}
        #import cProfile as profile
        #profile.runctx('webpush(sub_data,json.dumps(data),vapid_claims=claims,vapid_private_key=settings.PUSH_PRIVATE_KEY,)', globals(), locals(),"webpush.prof")
        res = webpush(sub_data,
                    json.dumps(data),
                    vapid_claims=claims,
                    vapid_private_key=settings.PUSH_PRIVATE_KEY,
                    )
        return res


@python_2_unicode_compatible
class AccountRequest(models.Model):
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta(object):
        ordering = ['-timestamp']

    def __str__(self):
        return u'{} ({}) - {}'.format(self.email, self.user, self.timestamp)


class RandomDrawLog(models.Model):
    delegation = models.ForeignKey(Delegation, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=200, default = 'pending', choices=(('pending','Pending'), ('received', 'Received'), ('failed', 'Failed')))
    tag = models.CharField(max_length=200, default='')

    def __str__(self):
        return u'{} - {}'.format(self.delegation, self.status)
