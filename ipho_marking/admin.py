# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
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
    list_display = ('position', 'question', 'name', 'max_points')


class MarkingAdmin(admin.ModelAdmin):
    search_fields = ('student', )
    list_filter = ('version', 'marking_meta__question', 'student__delegation')
    list_display = ('marking_meta', 'student', 'version', 'points')


admin.site.register(models.MarkingMeta, MarkingMetaAdmin)
admin.site.register(models.Marking, MarkingAdmin)
