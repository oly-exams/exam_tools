from datetime import timedelta
from django.utils import timezone
from ipho_poll.models import VotingRight, Voting, VotingChoice, CastedVote, VotingRoom

from .base_data import BaseDataCreator


class PollDataCreator(BaseDataCreator):
    def create_poll_voting(self, title, content, room_name, **choices):
        room = None
        if room_name is not None:
            room = VotingRoom.objects.get(name=room_name)

        voting, created = Voting.objects.get_or_create(
            title=title, defaults=dict(content=content, voting_room=room)
        )
        if not created:
            return voting, created

        voting.save()
        for key, val in choices.items():
            choice = VotingChoice(voting=voting, label=key, choice_text=val)
            choice.save()
            voting.votingchoice_set.add(choice)
        self.log(voting, "..", "created")
        return voting, created

    def create_voting_room(self, name, visibility=1):
        room, cre = VotingRoom.objects.get_or_create(name=name, visibility=visibility)
        if cre:
            self.log(room, "..", "created")
        return room

    @staticmethod
    def open_poll_voting_for_sec(voting, sec):
        voting.end_date = timezone.now() + timedelta(seconds=sec)
        voting.save()

    @staticmethod
    def close_poll_voting_with_result(voting, **result):
        voting.end_date = timezone.now()
        iterat = iter(VotingRight.objects.all())
        for key, val in result.items():
            choice = voting.votingchoice_set.get(label=key)
            for _ in range(val):
                voting_right = next(iterat)
                CastedVote.objects.create(
                    voting=voting, choice=choice, voting_right=voting_right
                )
        voting.save()
