# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from ipho_exam import qml

def question_points(root, part_num=-1, subq_num=0):
    ## This function is not too geenric, but it should fit our needs
    ret = []
    part_code = lambda num: chr(65+num)
    for obj in root.children:
        if isinstance(obj, QMLpart):
            part_num += 1
            subq_num = 0
        if isinstance(obj, QMLsubquestion):
            subq_num += 1
            points = float(obj.attributes['points']) if 'points' in obj.attributes else 0.
            ret.append(( '{}.{}'.format(part_code(part_num), subq_num), points ))
        child_points, part_num, subq_num = question_points(obj, part_num, subq_num)
        ret += child_points
    return ret, part_num, subq_num

def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    for node_name in ['VersionNode', 'TranslationNode']:
        NodeType = apps.get_model("ipho_exam", node_name)
        for node in NodeType.objects.using(db_alias).all():
            q = qml.QMLquestion(node.content)


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0049_auto_20160531_1923'),
    ]

    operations = [
            migrations.RunPython(forwards_func),
    ]
