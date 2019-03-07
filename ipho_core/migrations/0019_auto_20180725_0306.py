# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0018_randomdrawlog_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='randomdrawlog',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('received', 'Received'), ('failed', 'Failed')], default='pending', max_length=200),
        ),
    ]
