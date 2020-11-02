from datetime import timedelta
from django.utils import timezone
from ipho_poll.models import VotingRight, Question, Choice, Vote

from .base_data import BaseDataCreator


class QuestionDataCreator(BaseDataCreator):
    def create_question(self, title, content, **choices):
        que = Question.objects.create(title=title, content=content)
        que.save()
        for key, val in choices.items():
            choice = Choice(question=que, label=key, choice_text=val)
            choice.save()
            que.choice_set.add(choice)
        self.log(que, "..", "created")
        return que

    @staticmethod
    def open_question_for_sec(que, sec):
        que.end_date = timezone.now() + timedelta(seconds=sec)
        que.save()

    @staticmethod
    def close_question_with_result(que, **result):
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
