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


OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")

# exams = Exam.objects.filter(name__in=['Theory', 'Experiment'])
exams = Exam.objects.all()

questions = Question.objects.filter(exam__in=exams)

# languages = Language.objects.filter(name__contains='final')
languages = Language.objects.filter(
    delegation__name=OFFICIAL_DELEGATION, versioned=False
)
ss = StringIO()
save(languages, ss)
data = json.loads(ss.getvalue())
# for d in data:
#     d['fields']['delegation'] = [u'IPhO']
#     d['fields']['name'] = d['fields']['name'].replace(' final', '')
json.dump(data, open("035_trans_official_lang.json", "w"), indent=2)

nodes = TranslationNode.objects.filter(
    question__in=questions, language__in=languages
).all()
ss = StringIO()
save(nodes, ss)
data = json.loads(ss.getvalue())
# for d in data:
#     d['fields']['language'] = [d['fields']['language'][0].replace(' final', ''), u'IPhO']
json.dump(data, open("036_trans_official_nodes.json", "w"), indent=2)
