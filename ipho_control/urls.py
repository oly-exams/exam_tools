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

from django.urls import path

from . import views

app_name = "control"
urlpatterns = [
    path("cockpit", views.cockpit, name="cockpit"),
    path("cockpit/<int:exam_id>", views.cockpit, name="cockpit-id"),
    path(
        "cockpit/<int:exam_id>/changed-state",
        views.cockpit,
        kwargs={"changed_state": True},
        name="cockpit-changed-state",
    ),
    path(
        "cockpit/<int:exam_id>/deleted",
        views.cockpit,
        kwargs={"deleted_state": True},
        name="cockpit-deleted-state",
    ),
    path(
        "cockpit/switch-state/<int:exam_id>/<int:state_id>",
        views.switch_state,
        name="switch-state",
    ),
    path("cockpit/exam_history/<int:exam_id>", views.exam_history, name="exam-history"),
    path("state/add", views.add_edit_state, name="add-state"),
    path("state/edit/<int:state_id>", views.add_edit_state, name="edit-state"),
    path("state/delete/<int:state_id>", views.delete_state, name="delete-state"),
    path("state/summary", views.exam_state_summary, name="exam-state-summary"),
]
