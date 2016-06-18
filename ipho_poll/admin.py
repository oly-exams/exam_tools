from django.contrib import admin

from .models import Question, Choice, Vote, VotingRight

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Question information',	{'fields': ['title', 'content']}),
        ('Date information',		{'fields': ['pub_date', 'end_date'],
					 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('title', 'pub_date', 'end_date', 'vote_result', 'implementation')
    list_filter = ['pub_date', 'end_date', 'vote_result', 'implementation']
    search_fields = ['title', 'content']

class VoteAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Vote Information',                {'fields': ['question', 'choice', 'voting_right']}),
    ]
    list_display = ('question', 'choice', 'voting_right')

class VotingRightAdmin(admin.ModelAdmin):
    fieldsets = [
        ('VotingRight Information',          {'fields': ['user', 'name']})
    ]
    list_display = ('user', 'name')


admin.site.register(Question, QuestionAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(VotingRight, VotingRightAdmin)
