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

languages = Language.objects.exclude(delegation__name='IPhO').exclude(delegation__name='TTT')
save(languages, '037_delegation_langs.json')


nodes = TranslationNode.objects.filter(question=questions, language=languages)
save(languages, '038_delegation_nodes.json')
