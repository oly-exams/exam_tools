# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0021_auto_20151222_1835'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='direction',
            field=models.CharField(default=b'ltr', max_length=3, choices=[(b'ltr', b'Left-to-right'), (b'rtl', b'Right-to-left')]),
        ),
    ]
