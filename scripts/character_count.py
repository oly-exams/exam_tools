#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    14.07.2016 15:25:38 CEST
# File:    character_count.py

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
    translations = TranslationNode.objects.filter(
        question__exam__name='Theory',
        question__code='Q',
        language=language
    )
    return sum(get_count(t) for t in translations)
    
def get_submitted_langs():
    submissions = StudentSubmission.objects.filter(exam__name='Theory')
    return set(s.language for s in submissions)
    
if __name__ == '__main__':
    langs = get_submitted_langs()
    Result = collections.namedtuple('Result', ['lang', 'count'])
    res = [Result(lang=l, count=count_all(l)) for l in langs]
    
    for x in sorted(res, key=operator.attrgetter('count')):
        print '{0.lang}: {0.count}'.format(x)
