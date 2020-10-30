from django.contrib import admin

from ipho_control.models import ExamControlState, ExamControlHistory

# Register your models here.


class ExamControlStateAdmin(admin.ModelAdmin):
    list_display = ("name", "exam", "position", "exam_settings")
    list_filter = ("exam",)


class ExamControlHistoryAdmin(admin.ModelAdmin):
    list_display = ("exam", "timestamp", "to_state", "user")
    list_filter = ("exam",)


admin.site.register(ExamControlState, ExamControlStateAdmin)
admin.site.register(ExamControlHistory, ExamControlHistoryAdmin)
