from django.contrib import admin

from .models import Question, Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Question information',	{'fields': ['question_text', 'status']}),
        ('Date information',		{'fields': ['pub_date'],
					 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'status', 'pub_date')
    list_filter = ['pub_date', 'status']
    search_fields = ['question_text']

admin.site.register(Question, QuestionAdmin)
