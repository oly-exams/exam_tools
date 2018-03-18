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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import re
import os
import operator
import collections
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

from ipho_exam.models import *
from ipho_exam import qml

REPLACE_TOKENS = ['<[^<>]*>', r'\\raisebox{[^{}]*}\[[^\[\]]*\]\[[^\[\]]*\]', r'\\vspace{[^{}]*}*']


def get_count(translation):
    def get_text(xml_element):
        res = xml_element.text or u''
        for c in xml_element.getchildren():
            res += get_text(c)
        return res

    text = get_text(qml.make_qml(translation).make_xml())
    for token in REPLACE_TOKENS:
        text = re.sub(token, u'', text)
    return len(text)


def count_all(language):
    translations = TranslationNode.objects.filter(question__exam__name='Theory', question__code='Q', language=language)
    return sum(get_count(t) for t in translations)


def get_submitted_langs():
    submissions = StudentSubmission.objects.filter(exam__name='Theory')
    return set(s.language for s in submissions)


if __name__ == '__main__':
    langs = get_submitted_langs()
    Result = collections.namedtuple('Result', ['lang', 'count'])
    res = [Result(lang=l, count=count_all(l)) for l in langs]

    for x in sorted(res, key=operator.attrgetter('count')):
        print('{0.lang}: {0.count}'.format(x))
