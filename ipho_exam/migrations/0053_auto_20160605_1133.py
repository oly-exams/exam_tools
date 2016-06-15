# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0052_like'),
    ]

    operations = [
        migrations.RenameField(
            model_name='like',
            old_name='Feedback',
            new_name='feedback',
        ),
    ]
