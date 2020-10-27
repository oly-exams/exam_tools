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

from django.conf.urls import re_path

from . import views

app_name = "poll"
urlpatterns = [
    # staff urls
    re_path(r"^staff/$", views.staff_index, name="staff-index"),
    re_path(
        r"^staff/partials/(?P<qtype>\w+)$",
        views.staff_index_partial,
        name="staff-index-partials",
    ),
    re_path(
        r"^staff/question/(?P<question_pk>\d+)/set/result/(?P<result>\d+)$",
        views.staff_set_result,
        name="staff-set-result",
    ),
    re_path(
        r"^staff/question/(?P<question_pk>\d+)/set/impl/(?P<impl>\d+)$",
        views.staff_set_impl,
        name="staff-set-impl",
    ),
    re_path(
        r"^question/detail/(?P<question_pk>\d+)/$", views.question, name="question"
    ),
    re_path(
        r"^question/large/(?P<question_pk>\d+)/$",
        views.question_large,
        name="question_large",
    ),
    re_path(r"^question/add/$", views.add_question, name="add-question"),
    re_path(
        r"^question/(?P<question_pk>\d+)/delete/$",
        views.delete_question,
        name="delete-question",
    ),
    re_path(
        r"^question/(?P<question_pk>\d+)/edit/$",
        views.edit_question,
        name="edit-question",
    ),
    re_path(
        r"^question/(?P<question_pk>\d+)/$", views.set_end_date, name="set-end-date"
    ),
    re_path(
        r"^question/(?P<question_pk>\d+)/remove-end-date$",
        views.remove_end_date,
        name="remove-end-date",
    ),
    re_path(
        r"^question/(?P<question_pk>\d+)/close$",
        views.close_question,
        name="close-question",
    ),
    # delegation urls
    re_path(r"^$", views.voter_index, name="voter-index"),
    re_path(r"^err/(?P<err_id>\d+)$", views.voter_index, name="voter-index_err"),
    re_path(r"^voted/$", views.voted, name="voted"),
]
