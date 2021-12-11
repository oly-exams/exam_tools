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

from django.contrib import admin

from . import models


class MarkingMetaAdmin(admin.ModelAdmin):
    list_display = ("position", "question", "name", "max_points")


class MarkingAdmin(admin.ModelAdmin):
    search_fields = ("participant",)
    list_filter = ("version", "marking_meta__question", "participant__delegation")
    list_display = ("marking_meta", "participant", "version", "points")


@admin.action(description="Set status to 'In progress'")
def set_status_to_in_progress(modeladmin, request, queryset):  # pylint: disable=unused-argument
    queryset.update(status=models.MarkingAction.OPEN)

@admin.action(description="Set status to 'Submitted'")
def set_status_to_submitted(modeladmin, request, queryset):  # pylint: disable=unused-argument
    queryset.update(status=models.MarkingAction.SUBMITTED_FOR_MODERATION)

@admin.action(description="Set status to 'Locked'")
def set_status_to_locked(modeladmin, request, queryset):  # pylint: disable=unused-argument
    queryset.update(status=models.MarkingAction.LOCKED_BY_MODERATION)

@admin.action(description="Set status to 'Final'")
def set_status_to_final(modeladmin, request, queryset):  # pylint: disable=unused-argument
    queryset.update(status=models.MarkingAction.FINAL)

class MarkingActionAdmin(admin.ModelAdmin):
    list_display = ("question", "delegation", "status")
    list_filter = ("question", "delegation", "status")
    actions = [set_status_to_in_progress, set_status_to_submitted, set_status_to_locked, set_status_to_final]

admin.site.register(models.MarkingMeta, MarkingMetaAdmin)
admin.site.register(models.Marking, MarkingAdmin)
admin.site.register(models.MarkingAction, MarkingActionAdmin)
