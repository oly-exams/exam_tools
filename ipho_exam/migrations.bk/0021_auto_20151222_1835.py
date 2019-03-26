# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0020_auto_20151206_1741'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='versionnode',
            options={'ordering': ['-version', '-timestamp']},
        ),
    ]
