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

app_name = "marking"
urlpatterns = [
    ## Delegation views
    re_path(r"^$", views.delegation_summary, name="delegation-summary"),
    re_path(
        r"^export/exam/(?P<exam_id>\d+)$",
        views.delegation_export,
        name="delegation-export",
    ),
    re_path(
        r"^detail/(?P<stud_id>\d+)/question/(?P<question_id>\d+)$",
        views.delegation_stud_view,
        name="delegation-stud-detail",
    ),
    re_path(
        r"^detail_all/question/(?P<question_id>\d+)$",
        views.delegation_view_all,
        name="delegation-all-detail",
    ),
    re_path(
        r"^detail/(?P<stud_id>\d+)/question/(?P<question_id>\d+)/edit$",
        views.delegation_stud_edit,
        name="delegation-stud-detail-edit",
    ),
    re_path(
        r"^detail_all/question/(?P<question_id>\d+)/edit$",
        views.delegation_edit_all,
        name="delegation-all-detail-edit",
    ),
    re_path(
        r"^confirm/(?P<question_id>\d+)$",
        views.delegation_confirm,
        name="delegation-confirm",
    ),
    re_path(
        r"^confirm/final/(?P<question_id>\d+)$",
        views.delegation_confirm,
        name="delegation-final-confirm",
        kwargs={"final_confirmation": True},
    ),
    ## Markers
    re_path(
        r"^official/?$", views.official_marking_index, name="official-marking-index"
    ),
    re_path(
        r"^official/question/(?P<question_id>\d+)$",
        views.official_marking_index,
        name="official-marking-index-question",
    ),
    re_path(
        r"^official/question/(?P<question_id>\d+)/delegation/(?P<delegation_id>\d+)$",
        views.official_marking_detail,
        name="official-marking-detail",
    ),
    re_path(
        r"^official/question/(?P<question_id>\d+)/delegation/(?P<delegation_id>\d+)/confirmed$",
        views.official_marking_confirmed,
        name="official-marking-confirmed",
    ),
    ## Moderations views
    re_path(r"^moderate/?$", views.moderation_index, name="moderation-index"),
    re_path(
        r"^moderate/question/(?P<question_id>\d+)$",
        views.moderation_index,
        name="moderation-index-question",
    ),
    re_path(
        r"^moderate/question/(?P<question_id>\d+)/delegation/(?P<delegation_id>\d+)$",
        views.moderation_detail,
        name="moderation-detail",
    ),
    re_path(
        r"^moderate/question/(?P<question_id>\d+)/delegation/(?P<delegation_id>\d+)/confirmed$",
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
    re_path(
        r"^export-countries-to-moderate.csv$",
        views.export_countries_to_moderate,
        name="countries-to-moderate",
    ),
    re_path(r"^all/export.csv$", views.export, name="export"),
    re_path(r"^all/export-total.csv$", views.export_with_total, name="export-total"),
    re_path(
        r"^marking-submissions$", views.marking_submissions, name="marking-submissions"
    ),
    re_path(r"^progress$", views.progress, name="progress"),
]
