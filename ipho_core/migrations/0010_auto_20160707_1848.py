# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0009_auto_20160626_1205'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='delegation',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'ordering': ['code']},
        ),
    ]
