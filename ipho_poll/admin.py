# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
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
        ('Related feedbacks',	{'fields': ['feedbacks',]}),
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
