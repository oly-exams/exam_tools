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

from django.urls import path

from . import views

app_name = "control"
urlpatterns = [
    path("cockpit", views.cockpit, name="cockpit"),
    path("cockpit/<int:exam_id>", views.cockpit, name="cockpit-id"),
    path(
        "cockpit/<int:exam_id>/changed-phase",
        views.cockpit,
        kwargs={"changed_phase": True},
        name="cockpit-changed-phase",
    ),
    path(
        "cockpit/<int:exam_id>/deleted",
        views.cockpit,
        kwargs={"deleted_phase": True},
        name="cockpit-deleted-phase",
    ),
    path(
        "cockpit/switch-phase/<int:exam_id>/<int:phase_id>",
        views.switch_phase,
        name="switch-phase",
    ),
    path("cockpit/exam_history/<int:exam_id>", views.exam_history, name="exam-history"),
    path("phase/add/<int:exam_id>", views.add_edit_phase, name="add-phase"),
    path("phase/edit/<int:phase_id>", views.add_edit_phase, name="edit-phase"),
    path("phase/delete/<int:phase_id>", views.delete_phase, name="delete-phase"),
    path("phase/summary", views.exam_phase_summary, name="exam-phase-summary"),
]
