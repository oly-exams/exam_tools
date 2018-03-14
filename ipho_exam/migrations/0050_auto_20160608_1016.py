# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from ipho_exam import qml

def question_points(root, part_num=-1, subq_num=0):
    part_code = lambda num: chr(65+num)
    for obj in root.children:
        if isinstance(obj, qml.QMLpart):
            part_num += 1
            subq_num = 0
            if not 'Part' in obj.data:
                obj.data = 'Part {}: '.format(part_code(part_num)) + obj.data
        if isinstance(obj, qml.QMLsubquestion):
            subq_num += 1
            if not 'part_nr' in obj.attributes:
                obj.attributes['part_nr'] = part_code(part_num)
                obj.attributes['question_nr'] = str(subq_num)
        part_num, subq_num = question_points(obj, part_num, subq_num)
    return part_num, subq_num

def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    for node_name in ['VersionNode', 'TranslationNode']:
        NodeType = apps.get_model("ipho_exam", node_name)
        for node in NodeType.objects.using(db_alias).all():
            if not '<question' in node.text: continue
            q = qml.QMLquestion(node.text)
            question_points(q)
            node.text = qml.xml2string(q.make_xml())
            node.save()

def backwards_func(*args, **kwargs):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0049_auto_20160531_1923'),
    ]

    operations = [
            migrations.RunPython(forwards_func, backwards_func),
    ]
