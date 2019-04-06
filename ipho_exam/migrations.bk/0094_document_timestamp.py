# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0093_auto_20180606_2330'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='timestamp',
            field=models.DateTimeField(null=True, auto_now=True),
        ),
    ]
