from django.contrib import admin

from . import models


class MarkingMetaAdmin(admin.ModelAdmin):
    list_display = ("position", "question", "name", "max_points")


class MarkingAdmin(admin.ModelAdmin):
    search_fields = ("participant",)
    list_filter = ("version", "marking_meta__question", "participant__delegation")
    list_display = ("marking_meta", "participant", "version", "points")


@admin.action(description="Set status to 'In progress'")
def set_status_to_in_progress(
    modeladmin, request, queryset
):  # pylint: disable=unused-argument
    queryset.update(status=models.MarkingAction.OPEN)


@admin.action(description="Set status to 'Submitted'")
def set_status_to_submitted(
    modeladmin, request, queryset
):  # pylint: disable=unused-argument
    queryset.update(status=models.MarkingAction.SUBMITTED_FOR_MODERATION)


@admin.action(description="Set status to 'Locked'")
def set_status_to_locked(
    modeladmin, request, queryset
):  # pylint: disable=unused-argument
    queryset.update(status=models.MarkingAction.LOCKED_BY_MODERATION)


@admin.action(description="Set status to 'Final'")
def set_status_to_final(
    modeladmin, request, queryset
):  # pylint: disable=unused-argument
    queryset.update(status=models.MarkingAction.FINAL)


class MarkingActionAdmin(admin.ModelAdmin):
    list_display = ("question", "delegation", "status")
    list_filter = ("question", "delegation", "status")
    actions = [
        set_status_to_in_progress,
        set_status_to_submitted,
        set_status_to_locked,
        set_status_to_final,
    ]


admin.site.register(models.MarkingMeta, MarkingMetaAdmin)
admin.site.register(models.Marking, MarkingAdmin)
admin.site.register(models.MarkingAction, MarkingActionAdmin)
admin.site.register(models.QuestionPointsRescale)
