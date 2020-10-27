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

from django.urls import path, re_path

from . import views

app_name = "poll"
urlpatterns = [
    # staff urls
    path("staff/", views.staff_index, name="staff-index"),
    re_path(
        r"^staff/partials/(?P<qtype>\w+)$",
        views.staff_index_partial,
        name="staff-index-partials",
    ),
    path(
        "staff/question/<int:question_pk>/set/result/<int:result>",
        views.staff_set_result,
        name="staff-set-result",
    ),
    path(
        "staff/question/<int:question_pk>/set/impl/<int:impl>",
        views.staff_set_impl,
        name="staff-set-impl",
    ),
    path("question/detail/<int:question_pk>/", views.question, name="question"),
    path(
        "question/large/<int:question_pk/",
        views.question_large,
        name="question_large",
    ),
    path("question/add/", views.add_question, name="add-question"),
    path(
        "question/<int:question_pk>/delete/",
        views.delete_question,
        name="delete-question",
    ),
    path(
        "question/<int:question_pk>/edit/",
        views.edit_question,
        name="edit-question",
    ),
    path("question/<int:question_pk>/", views.set_end_date, name="set-end-date"),
    path(
        "question/<int:question_pk>/remove-end-date",
        views.remove_end_date,
        name="remove-end-date",
    ),
    path(
        "question/<int:question_pk>/close",
        views.close_question,
        name="close-question",
    ),
    # delegation urls
    path("", views.voter_index, name="voter-index"),
    path("err/<int:err_id>", views.voter_index, name="voter-index_err"),
    path("voted/", views.voted, name="voted"),
]
