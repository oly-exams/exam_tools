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
save(exams, '031_exams.json')

questions = Question.objects.filter(exam=exams)
save(questions, '032_questions.json')

figures = Figure.objects.all()
save_with_pk(figures, '033_figures.json')

nodes = VersionNode.objects.filter(question=questions).order_by('-version')
last_nodes = []
last_nodes_incl = []
for node in nodes:
    if node.question.pk in last_nodes_incl:
        continue
    last_nodes.append(node)
    last_nodes_incl.append(node.question.pk)
ss = StringIO()
save(last_nodes, ss)
data = json.loads(ss.getvalue())
for d in data:
    d['fields']['version'] = 1
    d['fields']['tag'] = 'initial'
json.dump(data, open('034_content_nodes.json', 'w'), indent=2)
