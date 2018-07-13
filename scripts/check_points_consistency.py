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

#!/usr/bin/env python

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'
import sys
sys.path.append(".")

from ipho_exam import qquery
from ipho_exam.models import Exam, Question

OFFICIAL_LANGUAGE_PK = 1


def check_question_answer_consistency(q1, q2):
    assert q1.position == q2.position
    assert set([q1.code, q2.code]) == {'Q', 'A'}
    version_node_1 = qquery.latest_version(q1.pk, OFFICIAL_LANGUAGE_PK).node
    version_node_2 = qquery.latest_version(q2.pk

def check_exam(exam):
    all_questions = Question.objects.filter(exam=exam, code__in=['Q', 'A']).order_by('position')
    for q1, q2 in zip(all_questions[::2], all_questions[1::2]):
        check_question_answer_consistency(q1=q1, q2=q2)


if __name__ == '__main__':
    for exam in Exam.objects.all():
        check_exam(exam)
