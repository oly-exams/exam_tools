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

from django.conf.urls import url

from . import views

urlpatterns = [
## Delegation views
    url(r'^/?$', views.delegation_summary, name='delegation-summary'),
    url(r'^export/exam/(?P<exam_id>\d+)$', views.delegation_export, name='delegation-export'),
    url(r'^detail/(?P<stud_id>\d+)/question/(?P<question_id>\d+)$', views.delegation_stud_view, name='delegation-stud-detail'),
    url(r'^detail_all/question/(?P<question_id>\d+)$', views.delegation_view_all, name='delegation-all-detail'),
    url(r'^detail/(?P<stud_id>\d+)/question/(?P<question_id>\d+)/edit$', views.delegation_stud_edit, name='delegation-stud-detail-edit'),
    url(r'^detail_all/question/(?P<question_id>\d+)/edit$', views.delegation_edit_all, name='delegation-all-detail-edit'),
    url(r'^confirm/(?P<exam_id>\d+)$', views.delegation_confirm, name='delegation-confirm'),

## Markers
# TODO
## Moderations views
    url(r'^moderate/?$', views.moderation_index, name='moderation-index'),
    url(r'^moderate/question/(?P<question_id>\d+)$', views.moderation_index, name='moderation-index-question'),
    url(r'^moderate/question/(?P<question_id>\d+)/delegation/(?P<delegation_id>\d+)$', views.moderation_detail, name='moderation-detail'),
    url(r'^moderate/question/(?P<question_id>\d+)/delegation/(?P<delegation_id>\d+)/confirmed$', views.moderation_confirmed, name='moderation-confirmed'),

##  staff views
    url(r'^staff/import/?$', views.import_exam, name='import-exam'),
    url(r'^staff/?$', views.summary, name='summary'),
    url(r'^staff/v(?P<version>\w)/student/(?P<stud_id>\d+)/question/(?P<question_id>\d+)/edit$', views.staff_stud_detail, name='staff-stud-detail'),

    url(r'^all/export.csv$', views.export, name='export'),
]
