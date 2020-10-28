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

app_name = "marking"
urlpatterns = [
    ## Delegation views
    path("", views.delegation_summary, name="delegation-summary"),
    path(
        "export/exam/<int:exam_id>",
        views.delegation_export,
        name="delegation-export",
    ),
    path(
        "detail/<int:stud_id>/question/<int:question_id>",
        views.delegation_stud_view,
        name="delegation-stud-detail",
    ),
    path(
        "detail_all/question/<int:question_id>",
        views.delegation_view_all,
        name="delegation-all-detail",
    ),
    path(
        "detail/<int:stud_id>/question/<int:question_id>/edit",
        views.delegation_stud_edit,
        name="delegation-stud-detail-edit",
    ),
    path(
        "detail_all/question/<int:question_id>/edit",
        views.delegation_edit_all,
        name="delegation-all-detail-edit",
    ),
    path(
        "confirm/<int:question_id>",
        views.delegation_confirm,
        name="delegation-confirm",
    ),
    path(
        "confirm/final/<int:question_id>",
        views.delegation_confirm,
        name="delegation-final-confirm",
        kwargs={"final_confirmation": True},
    ),
    ## Markers
    re_path(
        r"^official/?$", views.official_marking_index, name="official-marking-index"
    ),
    path(
        "official/question/<int:question_id>",
        views.official_marking_index,
        name="official-marking-index-question",
    ),
    path(
        "official/question/<int:question_id>/delegation/<int:delegation_id>",
        views.official_marking_detail,
        name="official-marking-detail",
    ),
    path(
        "official/question/<int:question_id>/delegation/<int:delegation_id>/confirmed",
        views.official_marking_confirmed,
        name="official-marking-confirmed",
    ),
    ## Moderations views
    re_path(r"^moderate/?$", views.moderation_index, name="moderation-index"),
    path(
        "moderate/question/<int:question_id>",
        views.moderation_index,
        name="moderation-index-question",
    ),
    path(
        "moderate/question/<int:question_id>/delegation/<int:delegation_id>",
        views.moderation_detail,
        name="moderation-detail",
    ),
    path(
        "moderate/question/<int:question_id>/delegation/<int:delegation_id>/confirmed",
        views.moderation_confirmed,
        name="moderation-confirmed",
    ),
    ##  staff views
    re_path(r"^staff/import/?$", views.import_exam, name="import-exam"),
    re_path(r"^staff/?$", views.summary, name="summary"),
    re_path(
        r"^staff/v(?P<version>\w)/student/(?P<stud_id>\d+)/question/(?P<question_id>\d+)/edit$",
        views.staff_stud_detail,
        name="staff-stud-detail",
    ),
    path(
        "export-countries-to-moderate.csv",
        views.export_countries_to_moderate,
        name="countries-to-moderate",
    ),
    path("all/export.csv", views.export, name="export"),
    path("all/export-total.csv", views.export_with_total, name="export-total"),
    path("marking-submissions", views.marking_submissions, name="marking-submissions"),
    path("progress", views.progress, name="progress"),
]
