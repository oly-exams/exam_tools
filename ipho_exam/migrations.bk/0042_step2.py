# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0041_step1'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='type',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='type_num',
            new_name='type',
        ),
    ]
