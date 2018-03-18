# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
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

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'ipho_poll.views',
    # staff urls
    url(r'^staff/$', 'staffIndex', name='staffIndex'),
    url(r'^staff/partials/(?P<qtype>\w+)$', 'staffIndexPartial', name='staff-index-partials'),
    url(
        r'^staff/question/(?P<question_pk>\d+)/set/result/(?P<result>\d+)$', 'staff_setResult', name='staff-set-result'
    ),
    url(r'^staff/question/(?P<question_pk>\d+)/set/impl/(?P<impl>\d+)$', 'staff_setImpl', name='staff-set-impl'),
    url(r'^question/detail/(?P<question_pk>\d+)/$', 'question', name='question'),
    url(r'^question/large/(?P<question_pk>\d+)/$', 'question_large', name='question_large'),
    url(r'^question/add/$', 'addQuestion', name='addQuestion'),
    url(r'^question/(?P<question_pk>\d+)/delete/$', 'deleteQuestion', name='deleteQuestion'),
    url(r'^question/(?P<question_pk>\d+)/edit/$', 'editQuestion', name='editQuestion'),
    url(r'^question/(?P<question_pk>\d+)/$', 'setEndDate', name='setEndDate'),
    url(r'^question/(?P<question_pk>\d+)/removeEndDate$', 'removeEndDate', name='removeEndDate'),

    #delegation urls
    url(r'^$', 'voterIndex', name='voterIndex'),
    url(r'^voted/$', 'voted', name='voted'),
)
