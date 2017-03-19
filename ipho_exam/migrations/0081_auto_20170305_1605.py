# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def copy_content_params(apps, schema_editor):
    CompiledFigure = apps.get_model('ipho_exam', 'CompiledFigure')
    for cf in CompiledFigure.objects.all():
        cf.params = cf.tmp_params
        cf.content = cf.tmp_content
        cf.save()

class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0080_auto_20170305_1555'),
    ]

    operations = [
        migrations.RenameField('Figure', 'content', 'tmp_content'),
        migrations.RenameField('Figure', 'params', 'tmp_params'),
        migrations.AddField(
            model_name='compiledfigure',
            name='content',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='compiledfigure',
            name='params',
            field=models.TextField(blank=True),
        ),
        migrations.RunPython(copy_content_params),
    ]
