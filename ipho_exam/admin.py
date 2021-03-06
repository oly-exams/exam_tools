# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
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

from builtins import object
from django.contrib import admin
from django import forms
import json
from ipho_exam.models import Language, Exam, Question, VersionNode, TranslationNode, PDFNode, Figure, Feedback, Like, StudentSubmission, ExamAction, TranslationImportTmp, Document, DocumentTask, Place, AttributeChange
from django_ace import AceWidget

# Register your models here.


class VersionNodeAdminForm(forms.ModelForm):
    text = forms.CharField(widget=AceWidget(mode='xml', wordwrap=True, width='100%'))

    class Meta(object):
        model = VersionNode
        fields = '__all__'


        # widgets = {
        #     'body':AceWidget()
        # }
class FigureAdminForm(forms.ModelForm):
    content = forms.CharField(widget=AceWidget(mode='xml', wordwrap=True, width='100%'))

    class Meta(object):
        model = Figure
        fields = '__all__'


class AttributeChangeForm(forms.ModelForm):
    class Meta(object):
        model = AttributeChange
        fields = '__all__'

    def clean(self):
        super(AttributeChangeForm, self).clean()
        try:
            d = json.loads(self.cleaned_data['content'])
            self.cleaned_data['content'] = json.dumps(d, indent=2)
        except ValueError:
            raise forms.ValidationError("Content is not valid JSON.")
        return self.cleaned_data


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2


class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'marking_active', 'moderation_active', 'hidden')
    inlines = [QuestionInline]


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam', 'feedback_active', 'position')
    list_filter = ('exam', )


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'delegation', 'font', 'is_pdf')
    list_filter = ('delegation', 'font')
    search_fields = ['name']


class VersionNodeAdmin(admin.ModelAdmin):
    form = VersionNodeAdminForm
    list_display = ('question', 'language', 'version', 'tag', 'status', 'timestamp')
    list_filter = ('question', )


class TranslationNodeAdmin(admin.ModelAdmin):
    list_display = ('question', 'language', 'status', 'timestamp')
    list_filter = ('question', 'language__delegation')


class AttributeChangeAdmin(admin.ModelAdmin):
    form = AttributeChangeForm
    list_display = ('node', )
    list_filter = ('node__question', 'node__language')


class PDFNodeAdmin(admin.ModelAdmin):
    list_display = ('question', 'language', 'status', 'timestamp')
    list_filter = ('question', 'language__delegation')


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('question', 'part', 'delegation', 'comment', 'status', 'timestamp')
    list_filter = ('question', 'delegation', 'status')


class LikeAdmin(admin.ModelAdmin):
    list_display = ('status', 'feedback', 'delegation')


class FigureAdmin(admin.ModelAdmin):
    form = FigureAdminForm
    list_display = ('pk', 'name')


class CompiledFigureAdmin(admin.ModelAdmin):
    form = FigureAdminForm
    list_display = ('pk', 'name', 'params')


class StudentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'language', 'with_answer')


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam', 'student')
    list_filter = ('exam', 'student__delegation')


class ExamActionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'delegation', 'action', 'status', 'timestamp')
    list_filter = ('action', 'exam', 'delegation')


class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'exam', 'position', 'student', 'num_pages', 'barcode_num_pages', 'extra_num_pages', 'barcode_base',
        'scan_status'
    )
    list_filter = ('exam', 'position', 'student__delegation', 'scan_status')


admin.site.register(Language, LanguageAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(VersionNode, VersionNodeAdmin)
admin.site.register(TranslationNode, TranslationNodeAdmin)
admin.site.register(AttributeChange, AttributeChangeAdmin)
admin.site.register(PDFNode, PDFNodeAdmin)
admin.site.register(TranslationImportTmp)
admin.site.register(Figure, FigureAdmin)
admin.site.register(ExamAction, ExamActionAdmin)
admin.site.register(StudentSubmission, StudentSubmissionAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentTask)
