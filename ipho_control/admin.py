from django.contrib import admin

from ipho_control.models import (
    ExamState,
)

# Register your models here.


class ExamStateAdmin(admin.ModelAdmin):
    list_display = ("name", "exam", "position", "exam_settings")
    list_filter = ("exam",)


admin.site.register(ExamState, ExamStateAdmin)
