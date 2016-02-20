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
