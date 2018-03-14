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
from io import StringIO

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

def serialize(objs, with_pk):
  ss = StringIO()
  if with_pk:
    save_with_pk(objs, ss)
  else:
    save(objs, ss)
  return ss.getvalue()

orig_exam = 'Experiment - 2016'
dest_exam = 'Experiment - Short'

all_data = []

exams = Exam.objects.filter(name=orig_exam)
s = serialize(exams, with_pk=False)
s = s.replace(orig_exam, dest_exam)
all_data += json.loads(s)

questions = Question.objects.filter(exam=exams)
s = serialize(questions, with_pk=False)
s = s.replace(orig_exam, dest_exam)
all_data += json.loads(s)

nodes = VersionNode.objects.filter(question=questions).order_by('-version')
s = serialize(nodes, with_pk=False)
s = s.replace(orig_exam, dest_exam)
all_data += json.loads(s)


json.dump(all_data, open('duplicate_question.json', 'w'), indent=2)
