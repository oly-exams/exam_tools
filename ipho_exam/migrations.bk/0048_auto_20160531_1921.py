# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0047_remove_id_from_question_qml'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='code',
            field=models.CharField(default='E', max_length=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='code',
            field=models.CharField(default='Q', max_length=8),
            preserve_default=False,
        ),
    ]
