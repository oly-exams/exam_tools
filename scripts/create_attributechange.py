#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage: ./create_attributechange.py <delegation_name> <language_name> <question_pk>
"""

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)

import django
django.setup()

from ipho_exam.models import AttributeChange, TranslationNode

delegation_name, language_name, question_pk = sys.argv[1:]

question_pk = int(question_pk)

translation_node = TranslationNode.objects.get(
    language__delegation__name=delegation_name, language__name=language_name, question__pk=question_pk
)
attribute_change = AttributeChange.objects.create(node=translation_node)

print('Created AttributeChange with pk={}'.format(attribute_change.pk))
