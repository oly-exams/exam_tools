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

from django.conf.urls import url

from . import views

app_name = "poll"
urlpatterns = [
    # staff urls
    url(r"^staff/$", views.staffIndex, name="staffIndex"),
    url(
        r"^staff/partials/(?P<qtype>\w+)$",
        views.staffIndexPartial,
        name="staff-index-partials",
    ),
    url(
        r"^staff/question/(?P<question_pk>\d+)/set/result/(?P<result>\d+)$",
        views.staff_setResult,
        name="staff-set-result",
    ),
    url(
        r"^staff/question/(?P<question_pk>\d+)/set/impl/(?P<impl>\d+)$",
        views.staff_setImpl,
        name="staff-set-impl",
    ),
    url(r"^question/detail/(?P<question_pk>\d+)/$", views.question, name="question"),
    url(
        r"^question/large/(?P<question_pk>\d+)/$",
        views.question_large,
        name="question_large",
    ),
    url(r"^question/add/$", views.addQuestion, name="addQuestion"),
    url(
        r"^question/(?P<question_pk>\d+)/delete/$",
        views.deleteQuestion,
        name="deleteQuestion",
    ),
    url(
        r"^question/(?P<question_pk>\d+)/edit/$",
        views.editQuestion,
        name="editQuestion",
    ),
    url(r"^question/(?P<question_pk>\d+)/$", views.setEndDate, name="setEndDate"),
    url(
        r"^question/(?P<question_pk>\d+)/removeEndDate$",
        views.removeEndDate,
        name="removeEndDate",
    ),
    url(
        r"^question/(?P<question_pk>\d+)/close$",
        views.closeQuestion,
        name="closeQuestion",
    ),
    # delegation urls
    url(r"^$", views.voterIndex, name="voterIndex"),
    url(r"^err/(?P<err_id>\d+)$", views.voterIndex, name="voterIndex_err"),
    url(r"^voted/$", views.voted, name="voted"),
]
