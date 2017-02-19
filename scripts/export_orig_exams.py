# Exam Tools
#    
# Copyright (C) 2014 - 2017 Oly Exams Team
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
