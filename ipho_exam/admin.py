from django.contrib import admin
from django import forms
from ipho_exam.models import Language, Exam, Question, VersionNode, TranslationNode, Figure, Feedback, StudentSubmission, ExamDelegationSubmission
from ipho_exam.widgets import AceWidget

# Register your models here.

class VersionNodeAdminForm(forms.ModelForm):
    text = forms.CharField(widget=AceWidget(mode='xml', width='100%'))
    class Meta:
        model = VersionNode
        fields = '__all__'
        # widgets = {
        #     'body':AceWidget()
        # }
class FigureAdminForm(forms.ModelForm):
    content = forms.CharField(widget=AceWidget(mode='xml', width='100%'))
    class Meta:
        model = Figure
        fields = '__all__'

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2

class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'feedback_active', 'hidden')
    inlines = [QuestionInline]

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam', 'position')

class VersionNodeAdmin(admin.ModelAdmin):
    form = VersionNodeAdminForm
    list_display = ('question', 'language', 'version', 'status', 'timestamp')

class TranslationNodeAdmin(admin.ModelAdmin):
    list_display = ('question', 'language', 'status', 'timestamp')

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('question', 'delegation', 'comment', 'status', 'timestamp')

class FigureAdmin(admin.ModelAdmin):
    form = FigureAdminForm

class StudentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('exam','student','language','with_answer')

class ExamDelegationSubmissionAdmin(admin.ModelAdmin):
    list_display = ('exam','delegation','status','timestamp')

admin.site.register(Language)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(VersionNode, VersionNodeAdmin)
admin.site.register(TranslationNode, TranslationNodeAdmin)
admin.site.register(Figure, FigureAdmin)
admin.site.register(ExamDelegationSubmission, ExamDelegationSubmissionAdmin)
admin.site.register(StudentSubmission, StudentSubmissionAdmin)
