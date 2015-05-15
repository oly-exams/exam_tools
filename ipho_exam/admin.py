from django.contrib import admin
from ipho_exam.models import Language, Exam, Question, VersionNode, TranslationNode, Figure

# Register your models here.

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2

class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'hidden')
    inlines = [QuestionInline]

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam', 'position')

class VersionNodeAdmin(admin.ModelAdmin):
    list_display = ('question', 'language', 'version', 'status', 'timestamp')

class TranslationNodeAdmin(admin.ModelAdmin):
    list_display = ('question', 'language', 'status', 'timestamp')


admin.site.register(Language)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(VersionNode, VersionNodeAdmin)
admin.site.register(TranslationNode, TranslationNodeAdmin)
admin.site.register(Figure)
