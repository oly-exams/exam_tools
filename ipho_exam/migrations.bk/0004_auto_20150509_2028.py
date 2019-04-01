# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0003_auto_20150222_2101'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='extraheader',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='language',
            name='polyglossia',
            field=models.CharField(default='english', max_length=100),
            preserve_default=False,
        ),
    ]
