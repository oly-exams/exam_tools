from django.contrib import admin

from . import models

class MarkingMetaAdmin(admin.ModelAdmin):
    list_display = ('position','question','name','max_points')

class MarkingAdmin(admin.ModelAdmin):
    search_fields = ('student',)
    list_filter = ('version', 'marking_meta__question', 'student__delegation')
    list_display = ('marking_meta','student','version','points')

admin.site.register(models.MarkingMeta, MarkingMetaAdmin)
admin.site.register(models.Marking, MarkingAdmin)
