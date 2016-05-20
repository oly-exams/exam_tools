# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_marking', '0005_auto_20160430_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marking',
            name='points',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
