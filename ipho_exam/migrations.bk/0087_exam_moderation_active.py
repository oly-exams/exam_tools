# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0086_auto_20170325_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='moderation_active',
            field=models.BooleanField(default=False, help_text=b'Allow access to moderation interface.'),
        ),
    ]
