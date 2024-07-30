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
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exam_tools.settings")
sys.path.append('.')

django.setup()


from ipho_exam.models import Delegation, Exam, ExamAction, Question
from ipho_marking.models import MarkingAction

for exam in Exam.objects.all():
    for delegation in Delegation.objects.all():
        for action, _ in ExamAction.ACTION_CHOICES:
            exam_action, _ = ExamAction.objects.get_or_create(
                exam=exam, delegation=delegation, action=action
            )

for question in Question.objects.filter(type=Question.ANSWER).all():
    for delegation in Delegation.objects.all():
        MarkingAction.objects.get_or_create(question=question, delegation=delegation)
