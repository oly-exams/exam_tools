# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ipho_exam.utils.natural_id
from ipho_exam import qml
from ipho_exam.qml import QMLfigure, make_qml

def migrate_figid(apps, qml_obj):
    Figure = apps.get_model('ipho_exam', 'Figure')
    if isinstance(qml_obj, QMLfigure):
        fig = Figure.objects.get(pk=int(qml_obj.attributes['figid']))
        qml_obj.attributes['figid'] = fig.natural_key
    for child in qml_obj.children:
        migrate_figid(apps, child)

def forwards_func(apps, schema_editor):
    Figure = apps.get_model('ipho_exam', 'Figure')
    for fig in Figure.objects.all():
        fig.natural_key = ipho_exam.utils.natural_id.generate_id()
        fig.save()

    VersionNode = apps.get_model('ipho_exam', 'VersionNode')
    for version_node in VersionNode.objects.all():
        version_qml = make_qml(version_node)
        migrate_figid(apps, version_qml)
        version_node.text = qml.xml2string(version_qml.make_xml())
        version_node.save()

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
            field=models.CharField(
                max_length=100,
                db_index=True,
                blank=True
            ),
        ),
        migrations.RunPython(forwards_func, backwards_func),
        migrations.AlterField(
            model_name='figure',
            name='natural_key',
            field=models.CharField(
                max_length=100,
                db_index=True,
                blank=False,
                unique=True
            ),
        )
    ]
