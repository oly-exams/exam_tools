# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ipho_exam.utils.natural_id

def forwards_func(apps, schema_editor):
    Figure = apps.get_model('ipho_exam', 'Figure')
    for fig in Figure.objects.all():
        fig.natural_key = ipho_exam.utils.natural_id.generate_id()
        fig.save()

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
