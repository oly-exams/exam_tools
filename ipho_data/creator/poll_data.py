from datetime import timedelta
from django.utils import timezone
from ipho_poll.models import VotingRight, Question, Choice, Vote, VotingRoom

from .base_data import BaseDataCreator


class PollDataCreator(BaseDataCreator):
    def create_poll_que(self, title, content, room_name, **choices):
        room = None
        if room_name is not None:
            room = VotingRoom.objects.get(name=room_name)
        que = Question.objects.create(title=title, content=content, voting_room=room)
        que.save()
        for key, val in choices.items():
            choice = Choice(question=que, label=key, choice_text=val)
            choice.save()
            que.choice_set.add(choice)
        self.log(que, "..", "created")
        return que

    def create_voting_room(self, name, visibility=1):
        room, cre = VotingRoom.objects.get_or_create(name=name, visibility=visibility)
        if cre:
            self.log(room, "..", "created")
        return room

    @staticmethod
    def open_poll_que_for_sec(que, sec):
        que.end_date = timezone.now() + timedelta(seconds=sec)
        que.save()

    @staticmethod
    def close_poll_que_with_result(que, **result):
        que.end_date = timezone.now()
        iterat = iter(VotingRight.objects.all())
        for key, val in result.items():
            choice = que.choice_set.get(label=key)
            for _ in range(val):
                voting_right = next(iterat)
                Vote.objects.create(
                    question=que, choice=choice, voting_right=voting_right
                )
        que.save()
