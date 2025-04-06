import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
sys.path.append(".")

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exam_tools.settings")
sys.path.append(".")

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
