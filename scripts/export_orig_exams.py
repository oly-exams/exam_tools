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


def save_with_pk(objs, fname):
    serializers.serialize('json', objs, indent=2,
            use_natural_foreign_keys=False,
            use_natural_primary_keys=False,
            stream=open(fname, 'w'))

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
save(last_nodes, '034_content_nodes.json')
