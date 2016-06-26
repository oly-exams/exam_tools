# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0064_auto_20160623_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='scan_msg',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='document',
            name='scan_status',
            field=models.CharField(blank=True, max_length=10, null=True, choices=[(b'S', b'Success'), (b'W', b'Warning'), (b'M', b'Missing pages')]),
        ),
    ]
