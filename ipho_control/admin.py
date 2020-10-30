from django.contrib import admin

from ipho_control.models import ExamState, ExamHistory

# Register your models here.


class ExamStateAdmin(admin.ModelAdmin):
    list_display = ("name", "exam", "position", "exam_settings")
    list_filter = ("exam",)


class ExamHistoryAdmin(admin.ModelAdmin):
    list_display = ("exam", "timestamp", "to_state", "user")
    list_filter = ("exam",)


admin.site.register(ExamState, ExamStateAdmin)
admin.site.register(ExamHistory, ExamHistoryAdmin)
