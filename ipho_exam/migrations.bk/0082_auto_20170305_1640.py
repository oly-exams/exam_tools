# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0081_auto_20170305_1605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='figure',
            name='tmp_content',
        ),
        migrations.RemoveField(
            model_name='figure',
            name='tmp_params',
        ),
    ]
