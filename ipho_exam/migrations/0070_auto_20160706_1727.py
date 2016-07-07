# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from ipho_exam import qml

def update_question(root):
    for obj in root.children:
        if isinstance(obj, qml.QMLpart):
            if not 'points' in obj.data:
                obj.data = u'{} ({} points)'.format(obj.data, obj.attributes['points'])
        if isinstance(obj, qml.QMLtitle):
            if not 'points' in obj.data:
                obj.data = u'{} ({} points)'.format(obj.data, 10)
        update_question(obj)

def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    for node_name in ['VersionNode', 'TranslationNode']:
        NodeType = apps.get_model("ipho_exam", node_name)
        for node in NodeType.objects.using(db_alias).all():
            if not '<question' in node.text: continue
            try:
                q = qml.QMLquestion(node.text)
                update_question(q)
                node.text = qml.xml2string(q.make_xml())
                node.save()
            except:
                pass

def backwards_func(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0069_document_extra_num_pages'),
    ]

    operations = [
            migrations.RunPython(forwards_func, backwards_func),
    ]
