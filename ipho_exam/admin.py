from django.contrib import admin
from ipho_exam.models import Language, Exam, Question, VersionNode, TranslationNode

# Register your models here.

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2

class ExamAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]


admin.site.register(Language)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Question)
admin.site.register(VersionNode)
admin.site.register(TranslationNode)
