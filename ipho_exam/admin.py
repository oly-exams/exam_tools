from django.contrib import admin
from django import forms
from ipho_exam.models import Language, Exam, Question, VersionNode, TranslationNode, PDFNode, Figure, Feedback, Like, StudentSubmission, ExamAction, TranslationImportTmp, Document, DocumentTask, Place, AttributeChange
from ipho_exam.widgets import AceWidget

# Register your models here.

class VersionNodeAdminForm(forms.ModelForm):
    text = forms.CharField(widget=AceWidget(mode='xml', wordwrap=True, width='100%'))
    class Meta:
        model = VersionNode
        fields = '__all__'
        # widgets = {
        #     'body':AceWidget()
        # }
class FigureAdminForm(forms.ModelForm):
    content = forms.CharField(widget=AceWidget(mode='xml', wordwrap=True, width='100%'))
    class Meta:
        model = Figure
        fields = '__all__'

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2

class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'marking_active', 'hidden')
    inlines = [QuestionInline]

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam', 'feedback_active', 'position')
    list_filter = ('exam',)

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'delegation', 'font', 'is_pdf')
    list_filter = ('delegation', 'font')
    search_fields = ['name']

class VersionNodeAdmin(admin.ModelAdmin):
    form = VersionNodeAdminForm
    list_display = ('question', 'language', 'version', 'tag', 'status', 'timestamp')
    list_filter = ('question',)

class TranslationNodeAdmin(admin.ModelAdmin):
    list_display = ('question', 'language', 'status', 'timestamp')
    list_filter = ('question','language__delegation')

class AttributeChangeAdmin(admin.ModelAdmin):
    list_display = ('node', 'language')
    list_filter = ('node__question','language__delegation')

class PDFNodeAdmin(admin.ModelAdmin):
    list_display = ('question', 'language', 'status', 'timestamp')
    list_filter = ('question','language__delegation')

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('question', 'part', 'delegation', 'comment', 'status', 'timestamp')
    list_filter = ('question','delegation', 'status')

class LikeAdmin(admin.ModelAdmin):
    list_display = ('status', 'feedback', 'delegation')

class FigureAdmin(admin.ModelAdmin):
    form = FigureAdminForm
    list_display = ('pk', 'name', 'params')

class StudentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('exam','student','language','with_answer')

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name','exam','student')
    list_filter = ('exam', 'student__delegation')

class ExamActionAdmin(admin.ModelAdmin):
    list_display = ('exam','delegation','action','status','timestamp')
    list_filter = ('action','exam','delegation')

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('exam','position','student','num_pages', 'barcode_num_pages', 'extra_num_pages', 'barcode_base', 'scan_status')
    list_filter = ('exam','position','student__delegation', 'scan_status')

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
