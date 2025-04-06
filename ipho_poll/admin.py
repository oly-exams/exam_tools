from django.contrib import admin

from .models import CastedVote, Voting, VotingChoice, VotingRight, VotingRoom


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
