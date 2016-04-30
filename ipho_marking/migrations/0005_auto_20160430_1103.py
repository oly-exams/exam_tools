# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_marking', '0004_auto_20160430_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marking',
            name='comment',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='marking',
            name='points',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='markingmeta',
            name='name',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='markingmeta',
            name='position',
            field=models.PositiveSmallIntegerField(default=10, help_text=b'Sorting index inside one question'),
        ),
        migrations.AlterUniqueTogether(
            name='markingmeta',
            unique_together=set([('question', 'name')]),
        ),
    ]
