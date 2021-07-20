# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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
    path("staff/room/<int:room_id>", views.staff_index, name="staff-index_room"),
    re_path(
        r"^staff/room/(?P<room_id>\d*)/partials/(?P<qtype>\w+)$",
        views.staff_index_partial,
        name="staff-index-partials",
    ),
    path(
        "staff/voting/<int:voting_pk>/set/result/<int:result>",
        views.staff_set_result,
        name="staff-set-result",
    ),
    path(
        "staff/voting/<int:voting_pk>/set/impl/<int:impl>",
        views.staff_set_impl,
        name="staff-set-impl",
    ),
    path("voting/detail/<int:voting_pk>/", views.voting_details, name="voting"),
    path(
        "voting/large/<int:voting_pk>/",
        views.voting_large,
        name="voting_large",
    ),
    re_path(r"^voting/add/room/(?P<room_id>\d*)$", views.add_voting, name="add-voting"),
    path(
        "voting/<int:voting_pk>/delete/",
        views.delete_voting,
        name="delete-voting",
    ),
    path(
        "voting/<int:voting_pk>/edit/",
        views.edit_voting,
        name="edit-voting",
    ),
    path("voting/<int:voting_pk>/", views.set_end_date, name="set-end-date"),
    path(
        "voting/<int:voting_pk>/add_minutes/<int:minutes>/",
        views.add_minutes,
        name="add-minutes",
    ),
    path(
        "voting/<int:voting_pk>/close",
        views.close_voting,
        name="close-voting",
    ),
    path("room/edit/<int:room_id>", views.edit_room, name="edit-room"),
    # delegation urls
    path("", views.voter_index, name="voter-index"),
    path("room/<int:room_id>", views.voter_index, name="voter-index_room"),
    path("err/<int:err_id>", views.voter_index, name="voter-index_err"),
    path(
        "room/<int:room_id>/err/<int:err_id>",
        views.voter_index,
        name="voter-index_room_err",
    ),
    path("voted/room/<int:room_id>", views.voted, name="voted_room"),
    path("voted/", views.voted, name="voted"),
]
