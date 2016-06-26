# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0065_auto_20160626_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='marking_active',
            field=models.BooleanField(default=False, help_text=b'Allow marking submission from delegations.'),
        ),
    ]
