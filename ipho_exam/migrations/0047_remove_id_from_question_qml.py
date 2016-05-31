# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import re

qpattern = re.compile(r'id="q(\d+)_')
def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    for node_name in ['VersionNode', 'TranslationNode']:
        NodeType = apps.get_model("ipho_exam", node_name)
        for node in NodeType.objects.using(db_alias).all():
            node.text = qpattern.sub('id="q0_', node.text)
            node.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0046_feedback_part'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
