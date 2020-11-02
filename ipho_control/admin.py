from django.contrib import admin

from ipho_control.models import ExamPhase, ExamPhaseHistory

# Register your models here.


class ExamPhaseAdmin(admin.ModelAdmin):
    list_display = ("name", "exam", "position", "exam_settings")
    list_filter = ("exam",)


class ExamPhaseHistoryAdmin(admin.ModelAdmin):
    list_display = ("exam", "timestamp", "to_phase", "user")
    list_filter = ("exam",)


admin.site.register(ExamPhase, ExamPhaseAdmin)
admin.site.register(ExamPhaseHistory, ExamPhaseHistoryAdmin)
