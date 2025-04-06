import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exam_tools.settings")
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

import django

django.setup()

import json
from io import StringIO

from django.core import serializers

from ipho_control.models import ExamPhase
from ipho_exam.models import Exam, ExamAction, Question, VersionNode


def serialize(objs):
    ss = StringIO()
    serializers.serialize(
        "json",
        objs,
        indent=2,
        use_natural_foreign_keys=True,
        use_natural_primary_keys=True,
        stream=ss,
    )
    return ss.getvalue()


all_data = []
for exam in Exam.objects.all():
    print(f"Cloning exam {exam}")
    orig_exam_name = exam.name
    dest_exam_name = orig_exam_name + " (copy)"

    s = serialize([exam])
    s = s.replace(orig_exam_name, dest_exam_name)
    all_data += json.loads(s)

    # exam_actions = ExamAction.objects.filter(exam=exam)
    # s = serialize(exam_actions)
    # s = s.replace(orig_exam_name, dest_exam_name)
    # all_data += json.loads(s)

    exam_phases = ExamPhase.objects.filter(exam=exam)
    s = serialize(exam_phases)
    s = s.replace(orig_exam_name, dest_exam_name)
    all_data += json.loads(s)

    questions = Question.objects.filter(exam=exam)
    s = serialize(questions)
    s = s.replace(orig_exam_name, dest_exam_name)
    all_data += json.loads(s)

    for question in questions:
        node = VersionNode.objects.filter(question=question).first()
        if node is not None:
            s = serialize([node])
            s = s.replace(orig_exam_name, dest_exam_name)
            all_data += json.loads(s)

json.dump(all_data, open("duplicate_exams.json", "w"), indent=2)
