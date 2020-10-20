# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
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
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
sys.path.append(".")

import django

django.setup()
from django.conf import settings

from django.core import serializers
from ipho_exam.models import *
import json
from io import StringIO


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

nodes = TranslationNode.objects.filter(question__in=questions, language=languages)
ss = StringIO()
save(nodes, ss)
data = json.loads(ss.getvalue())
# for d in data:
#     d['fields']['language'] = [d['fields']['language'][0].replace(' final', ''), u'IPhO']
json.dump(data, open("036_trans_official_nodes.json", "w"), indent=2)
