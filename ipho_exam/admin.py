from django.contrib import admin
from django import forms
from ipho_exam.models import Language, Exam, Question, VersionNode, TranslationNode, Figure
from ipho_exam.widgets import AceWidget

# Register your models here.

class VersionNodeAdminForm(forms.ModelForm):
    text = forms.CharField(widget=AceWidget(mode='xml', width='100%'))
    class Meta:
        model = VersionNode
        # widgets = {
        #     'body':AceWidget()
        # }
class FigureAdminForm(forms.ModelForm):
    content = forms.CharField(widget=AceWidget(mode='xml', width='100%'))
    class Meta:
        model = Figure

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2

class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'hidden')
    inlines = [QuestionInline]

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam', 'position')

class VersionNodeAdmin(admin.ModelAdmin):
    form = VersionNodeAdminForm
    list_display = ('question', 'language', 'version', 'status', 'timestamp')

class TranslationNodeAdmin(admin.ModelAdmin):
    list_display = ('question', 'language', 'status', 'timestamp')

class FigureAdmin(admin.ModelAdmin):
    form = FigureAdminForm


admin.site.register(Language)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(VersionNode, VersionNodeAdmin)
admin.site.register(TranslationNode, TranslationNodeAdmin)
admin.site.register(Figure, FigureAdmin)
