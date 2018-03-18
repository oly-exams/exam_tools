# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import Mapping

from django.db import migrations, models
import ipho_exam.utils.natural_id
from ipho_exam import qml
from ipho_exam.qml import QMLfigure, make_qml

def get_updated_figid(apps, figid):
    Figure = apps.get_model('ipho_exam', 'Figure')
    fig = Figure.objects.get(pk=int(figid))
    return fig.natural_key

def migrate_version_node(apps, qml_obj):
    if isinstance(qml_obj, QMLfigure):
        qml_obj.attributes['figid'] = get_updated_figid(apps, qml_obj.attributes['figid'])
    for child in qml_obj.children:
        migrate_version_node(apps, child)

def migrate_attr_change(apps, mapping):
    for key, value in mapping.items():
        if key == 'figid':
            mapping[key] = get_updated_figid(apps, value)
        elif isinstance(value, Mapping):
            migrate_attr_change(apps, mapping=value)

def forwards_func(apps, schema_editor):
    Figure = apps.get_model('ipho_exam', 'Figure')
    for fig in Figure.objects.all():
        fig.natural_key = ipho_exam.utils.natural_id.generate_id()
        fig.save()

    VersionNode = apps.get_model('ipho_exam', 'VersionNode')
    for version_node in VersionNode.objects.all():
        version_qml = make_qml(version_node)
        migrate_version_node(apps, version_qml)
        version_node.text = qml.xml2string(version_qml.make_xml())
        version_node.save()

    AttributeChange = apps.get_model('ipho_exam', 'AttributeChange')
    for attr_change in AttributeChange.objects.all():
        attr_change_mapping = json.loads(attr_change.content)
        migrate_attr_change(apps, attr_change_mapping)
        attr_change.content = json.dumps(attr_change_mapping)
        attr_change.save()

def backwards_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0089_merge'),
    ]

    operations = [
        # non-unique
        migrations.AddField(
            model_name='figure',
            name='natural_key',
            field=models.URLField(
                max_length=100,
                db_index=True,
                blank=True
            ),
        ),
        migrations.RunPython(forwards_func, backwards_func),
        migrations.AlterField(
            model_name='figure',
            name='natural_key',
            field=models.URLField(
                max_length=100,
                db_index=True,
                blank=False,
                unique=True
            ),
        )
    ]
