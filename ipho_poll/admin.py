# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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

from .models import Voting, VotingChoice, CastedVote, VotingRight, VotingRoom


class VotingChoiceInline(admin.TabularInline):
    model = VotingChoice
    extra = 2


class VotingAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Voting information", {"fields": ["title", "content", "voting_room"]}),
        (
            "Date information",
            {"fields": ["pub_date", "end_date"], "classes": ["collapse"]},
        ),
        (
            "Related feedbacks",
            {
                "fields": [
                    "feedbacks",
                ]
            },
        ),
    ]
    inlines = [VotingChoiceInline]
    list_display = (
        "title",
        "voting_room",
        "pub_date",
        "end_date",
        "vote_result",
        "implementation",
    )
    list_filter = [
        "voting_room",
        "pub_date",
        "end_date",
        "vote_result",
        "implementation",
    ]
    search_fields = ["title", "content"]


class CastedVoteAdmin(admin.ModelAdmin):
    fieldsets = [
        ("CastedVote Information", {"fields": ["voting", "choice", "voting_right"]}),
    ]
    list_display = ("voting", "choice", "voting_right")


class VotingRightAdmin(admin.ModelAdmin):
    fieldsets = [("VotingRight Information", {"fields": ["user", "name"]})]
    list_display = ("user", "name")


admin.site.register(Voting, VotingAdmin)
admin.site.register(CastedVote, CastedVoteAdmin)
admin.site.register(VotingRight, VotingRightAdmin)
admin.site.register(VotingRoom)
