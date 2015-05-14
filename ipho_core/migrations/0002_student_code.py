# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='code',
            field=models.CharField(default='', unique=True, max_length=10),
            preserve_default=False,
        ),
    ]
