# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
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

from __future__ import print_function

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)

import django
django.setup()

from ipho_poll.models import Question, Choice, Vote, VotingRight
import random


def main():
    votingRights = VotingRight.objects.all()
    question_dict = {
        'title': 'How do you do?',
        'content': 'Please answer the question',
        'end_date': '2016-04-27T13:57:00+00:00',
    }
    question = Question.objects.create(**question_dict)
    choice1_dict = {'question': question, 'label': 'A', 'choice_text': 'Fine, thanks.'}
    choice2_dict = {'question': question, 'label': 'B', 'choice_text': 'Comme ci, comme ca.'}
    choice3_dict = {'question': question, 'label': 'C', 'choice_text': 'What ever, maaan...'}
    choice1 = Choice.objects.create(**choice1_dict)
    choice2 = Choice.objects.create(**choice2_dict)
    choice3 = Choice.objects.create(**choice3_dict)

    question.save()
    choice1.save()
    choice2.save()
    choice3.save()

    for votingRight in VotingRight.objects.all():
        r = random.random()
        if r > 0.66:
            vote = Vote.objects.create(question=question, choice=choice1, voting_right=votingRight)
        elif r < 0.33:
            vote = Vote.objects.create(question=question, choice=choice2, voting_right=votingRight)
        else:
            vote = Vote.objects.create(question=question, choice=choice3, voting_right=votingRight)
            vote.save()
    return question.pk


if __name__ == '__main__':
    print(main())
