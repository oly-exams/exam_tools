# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_marking', '0003_auto_20160423_1633'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='markingmeta',
            options={'ordering': ['position']},
        ),
        migrations.AlterUniqueTogether(
            name='marking',
            unique_together=set([('marking_meta', 'student', 'version')]),
        ),
    ]
