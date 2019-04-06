# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0055_auto_20160619_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='versionnode',
            name='tag',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
