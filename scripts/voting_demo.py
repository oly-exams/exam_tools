# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
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


import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

import django

django.setup()

import random

from ipho_poll.models import CastedVote, Voting, VotingChoice, VotingRight


def main():
    votingRights = VotingRight.objects.all()
    voting_dict = {
        "title": "How do you do?",
        "content": "Please answer the question",
        "end_date": "2016-04-27T13:57:00+00:00",
    }
    voting = Voting.objects.create(**voting_dict)
    voting_choice_dict1 = {
        "voting": voting,
        "label": "A",
        "choice_text": "Fine, thanks.",
    }
    voting_choice_dict2 = {
        "voting": voting,
        "label": "B",
        "choice_text": "Comme ci, comme ca.",
    }
    voting_choice_dict3 = {
        "voting": voting,
        "label": "C",
        "choice_text": "What ever, maaan...",
    }
    voting_choice1 = VotingChoice.objects.create(**voting_choice_dict1)
    voting_choice2 = VotingChoice.objects.create(**voting_choice_dict2)
    voting_choice3 = VotingChoice.objects.create(**voting_choice_dict3)

    voting.save()
    voting_choice1.save()
    voting_choice2.save()
    voting_choice3.save()

    for votingRight in VotingRight.objects.all():
        r = random.random()
        if r > 0.66:
            vote = CastedVote.objects.create(
                voting=voting, choice=voting_choice1, voting_right=votingRight
            )
        elif r < 0.33:
            vote = CastedVote.objects.create(
                voting=voting, choice=voting_choice2, voting_right=votingRight
            )
        else:
            vote = CastedVote.objects.create(
                voting=voting, choice=voting_choice3, voting_right=votingRight
            )
            vote.save()
    return voting.pk


if __name__ == "__main__":
    print(main())
