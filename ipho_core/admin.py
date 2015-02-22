from django.contrib import admin
from ipho_core.models import Delegation, Student

# Register your models here.

class DelegationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    filter_horizontal = ('members',)

class StudentAdmin(admin.ModelAdmin):
    fields = ('code', ('first_name', 'last_name'), 'delegation',)
    list_display = ('code', 'last_name', 'first_name', 'delegation',)
    search_fields = ('last_name', 'first_name')
    list_editable = ('first_name', 'last_name', 'delegation')
    list_filter = ('delegation',)
    

admin.site.register(Delegation, DelegationAdmin)
admin.site.register(Student, StudentAdmin)
