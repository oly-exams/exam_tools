import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

from django.core import serializers
from ipho_exam.models import *

def save(objs, fname):
    serializers.serialize('json', objs, indent=2,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True,
            stream=open(fname, 'w'))


exams = Exam.objects.filter(name__in=['Theory', 'Experiment'])
save(exams, '031_exams.json')

quesions = Question.objects.filter(exam=exam)
save(quesions, '032_questions.json')

figures = Figure.objects.all()
save(figures, '033_figures.json')

nodes = VersionNode.objects.filter(question=questions).oder_by('-version')
last_nodes = []
last_nodes_incl = set()
for node in nodes:
    if node.pk in last_nodes_incl:
        continue
    last_nodes.append(node)
    last_nodes_incl.add(node.pk)
save(last_nodes, '034_content_nodes.json')
