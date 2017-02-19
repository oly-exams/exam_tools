# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
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
from ipho_core.models import Delegation, Student, AutoLogin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.

class AutoLoginInline(admin.StackedInline):
    model = AutoLogin
    can_delete = False
    verbose_name_plural = 'autologin'
class UserAdmin(BaseUserAdmin):
    inlines = (AutoLoginInline, )

class DelegationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    filter_horizontal = ('members',)

class StudentAdmin(admin.ModelAdmin):
    fields = ('code', ('first_name', 'last_name'), 'delegation',)
    list_display = ('code', 'last_name', 'first_name', 'delegation',)
    search_fields = ('last_name', 'first_name')
    list_editable = ('first_name', 'last_name', 'delegation')
    list_filter = ('delegation',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Delegation, DelegationAdmin)
admin.site.register(Student, StudentAdmin)
