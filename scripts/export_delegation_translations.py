import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
sys.path.append(".")

import django

django.setup()

import json
from io import StringIO

from django.conf import settings
from django.core import serializers

from ipho_exam.models import *


def save(objs, stream):
    if type(stream) == str:
        stream = open(stream, "w")
    serializers.serialize(
        "json",
        objs,
        indent=2,
        use_natural_foreign_keys=True,
        use_natural_primary_keys=True,
        stream=stream,
    )


def save_with_pk(objs, stream):
    if type(stream) == str:
        stream = open(stream, "w")
    serializers.serialize(
        "json",
        objs,
        indent=2,
        use_natural_foreign_keys=False,
        use_natural_primary_keys=False,
        stream=stream,
    )


# exams = Exam.objects.filter(name__in=['Theory', 'Experiment'])
exams = Exam.objects.all()
print("Exporting data for exams:", exams)

questions = Question.objects.all().filter(exam__in=exams)
print("Exporting data for questions:", questions)

languages = Language.objects.exclude(
    delegation__name__in=[settings.OFFICIAL_DELEGATION]
).exclude(delegation__name__contains="-")
save(languages, "037_delegation_langs.json")

nodes = TranslationNode.objects.filter(question__in=questions, language__in=languages)
ss = StringIO()
save(nodes, ss)
data = json.loads(ss.getvalue())
# for d in data:
#     d['fields']['question'][0] = d['fields']['question'][0].replace('instructions', 'Instructions')
json.dump(data, open("038_delegation_nodes.json", "w"), indent=2)
