from django.contrib import admin
from ipho_exam.models import Language, Exam, Question, VersionNode, TranslationNode

# Register your models here.

admin.site.register(Language)
admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(VersionNode)
admin.site.register(TranslationNode)
