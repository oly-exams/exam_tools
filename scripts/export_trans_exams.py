import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

from django.core import serializers
from ipho_exam.models import *
import json
from StringIO import StringIO

def save(objs, stream):
    if type(stream) == str:
        stream = open(stream, 'w')
    serializers.serialize('json', objs, indent=2,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True,
            stream=stream)


def save_with_pk(objs, stream):
    if type(stream) == str:
        stream = open(stream, 'w')
    serializers.serialize('json', objs, indent=2,
            use_natural_foreign_keys=False,
            use_natural_primary_keys=False,
            stream=stream)

exams = Exam.objects.filter(name__in=['Theory', 'Experiment'])

questions = Question.objects.filter(exam=exams)

languages = Language.objects.filter(name__contains='final')
ss = StringIO()
save(languages, ss)
data = json.loads(ss.getvalue())
for d in data:
    d['fields']['delegation'] = [u'IPhO']
    d['fields']['name'] = d['fields']['name'].replace(' final', '')
json.dump(data, open('035_trans_official_lang.json'), indent=2)


nodes = TranslationNode.objects.filter(question=questions, language=languages)
ss = StringIO()
save(nodes, ss)
data = json.loads(ss.getvalue())
for d in data:
    d['fields']['language'] = [d['fields']['language'][0].replace(' final', ''), u'IPhO']
json.dump(data, open('035_trans_official_nodes.json'), indent=2)
