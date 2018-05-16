# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0090_add-chinese-traditional-language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='status',
            field=models.CharField(max_length=1, default='S', choices=[('S', 'Submitted'), ('V', 'Scheduled for voting'), ('I', 'Implemented'), ('T', 'Settled')]),
        ),
    ]
