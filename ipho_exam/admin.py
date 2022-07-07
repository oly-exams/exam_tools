# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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

import json

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django_ace import AceWidget

from ipho_exam.models import (
    Delegation,
    Language,
    Exam,
    Participant,
    Question,
    VersionNode,
    TranslationNode,
    PDFNode,
    Figure,
    RawFigure,
    Feedback,
    FeedbackComment,
    Like,
    ParticipantSubmission,
    ExamAction,
    TranslationImportTmp,
    CachedAutoTranslation,
    Document,
    DocumentTask,
    Place,
    AttributeChange,
)

# Register your models here.


class VersionNodeAdminForm(forms.ModelForm):
    text = forms.CharField(widget=AceWidget(mode="xml", wordwrap=True, width="100%"))

    class Meta:
        model = VersionNode
        fields = "__all__"

        # widgets = {
        #     'body':AceWidget()
        # }


class TranslationNodeAdminForm(forms.ModelForm):
    text = forms.CharField(widget=AceWidget(mode="xml", wordwrap=True, width="100%"))

    class Meta:
        model = TranslationNode
        fields = "__all__"


class FigureAdminForm(forms.ModelForm):
    content = forms.CharField(widget=AceWidget(mode="xml", wordwrap=True, width="100%"))

    class Meta:
        model = Figure
        fields = "__all__"


class AttributeChangeForm(forms.ModelForm):
    class Meta:
        model = AttributeChange
        fields = "__all__"

    def clean(self):
        super().clean()
        try:
            data = json.loads(self.cleaned_data["content"])
            self.cleaned_data["content"] = json.dumps(data, indent=2)
        except ValueError:
            raise forms.ValidationError(  # pylint: disable=raise-missing-from
                "Content is not valid JSON."
            )
        return self.cleaned_data


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2


class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "flags",
        "visibility",
        "can_translate",
        "feedback",
        "submission_printing",
        "answer_sheet_scan_upload",
        "delegation_scan_access",
        "marking_organizer_can_see_delegation_marks",
        "marking_organizer_can_enter",
        "marking_delegation_can_see_organizer_marks",
        "marking_delegation_action",
        "moderation",
    )
    inlines = [QuestionInline]


class ParticipantAdminForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        if "exam" not in cleaned_data:
            raise ValidationError("exam cannot be empty!")

        for student in cleaned_data.get("students", []):
            if student.delegation != cleaned_data["delegation"]:
                raise ValidationError(
                    f"Student '{student}' must have the same Delegation as the Participant '{cleaned_data['code']} ({cleaned_data['exam']})'. Cross-delegation Participant-groups not supported!"
                )

            for participant in student.participant_set.filter(
                exam=cleaned_data["exam"]
            ):
                if participant.code != cleaned_data["code"]:
                    raise ValidationError(
                        f"Student '{student}' already in another Participant '{participant}'. Cannot be in more than one."
                    )

        return cleaned_data


class ParticipantAdmin(admin.ModelAdmin):
    form = ParticipantAdminForm
    list_display = (
        "code",
        "exam",
        "full_name",
        "is_group",
        "delegation",
    )
    search_fields = ("full_name",)
    list_editable = tuple()
    list_filter = ("delegation",)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("name", "exam", "feedback_status", "position", "flags")
    list_filter = ("exam",)


class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "delegation", "font", "is_pdf")
    list_filter = ("delegation", "font")
    search_fields = ["name"]


class VersionNodeAdmin(admin.ModelAdmin):
    form = VersionNodeAdminForm
    list_display = ("question", "language", "version", "tag", "status", "timestamp")
    list_filter = ("status", "version", "question", "tag")


class TranslationNodeAdmin(admin.ModelAdmin):
    form = TranslationNodeAdminForm
    list_display = ("question", "language", "status", "timestamp")
    list_filter = ("question", "language__delegation")


class AttributeChangeAdmin(admin.ModelAdmin):
    form = AttributeChangeForm
    list_display = ("node",)
    list_filter = ("node__question", "node__language")


class PDFNodeAdmin(admin.ModelAdmin):
    list_display = ("question", "language", "status", "timestamp")
    list_filter = ("question", "language__delegation")


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("question", "part", "delegation", "comment", "status", "timestamp")
    list_filter = ("question", "delegation", "status")


class FeedbackCommentAdmin(admin.ModelAdmin):
    list_display = ("feedback", "delegation", "comment", "timestamp")
    list_filter = ("feedback__question", "delegation")


class LikeAdmin(admin.ModelAdmin):
    list_display = ("status", "feedback", "delegation")


class FigureAdmin(admin.ModelAdmin):
    form = FigureAdminForm
    list_display = ("pk", "name")


class CompiledFigureAdmin(admin.ModelAdmin):
    form = FigureAdminForm
    list_display = ("pk", "name", "params")


class DelegationFilter(admin.SimpleListFilter):
    title = "delegation"
    parameter_name = "delegation"

    def lookups(self, request, model_admin):
        return ((d.name, d) for d in Delegation.objects.all())

    def queryset(self, request, queryset):
        value = self.value()

        if value is None:
            return queryset.order_by("participant")
        return queryset.filter(language__delegation__name=value).order_by("participant")


class ParticipantSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "participant",
        "delegation",
        "language",
        "with_question",
        "with_answer",
    )
    list_filter = ("participant__exam", DelegationFilter, "language")

    def delegation(self, obj):  # pylint: disable=no-self-use
        return obj.language.delegation


class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "participant")
    list_filter = ("participant__exam", "participant__delegation")


class ExamActionAdmin(admin.ModelAdmin):
    list_display = ("exam", "delegation", "action", "status", "timestamp")
    list_filter = ("action", "exam", "delegation")


class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "position",
        "participant",
        "num_pages",
        "barcode_num_pages",
        "extra_num_pages",
        "barcode_base",
        "scan_status",
    )
    list_filter = ("position", "participant__delegation", "scan_status")


admin.site.register(Language, LanguageAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(FeedbackComment, FeedbackCommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(VersionNode, VersionNodeAdmin)
admin.site.register(TranslationNode, TranslationNodeAdmin)
admin.site.register(AttributeChange, AttributeChangeAdmin)
admin.site.register(PDFNode, PDFNodeAdmin)
admin.site.register(TranslationImportTmp)
admin.site.register(CachedAutoTranslation)
admin.site.register(Figure, FigureAdmin)
admin.site.register(RawFigure)

admin.site.register(ExamAction, ExamActionAdmin)
admin.site.register(ParticipantSubmission, ParticipantSubmissionAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentTask)
