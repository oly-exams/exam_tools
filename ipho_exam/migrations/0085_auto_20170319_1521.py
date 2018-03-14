# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0084_rawfigure'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='code',
            field=models.CharField(
                help_text=b'e.g. Q for Question, A for Answer Sheet, G for General Instruction', max_length=8
            ),
        ),
        migrations.AlterField(
            model_name='versionnode',
            name='tag',
            field=models.CharField(help_text=b'leave empty to show no tag', max_length=100, null=True, blank=True),
        ),
    ]
