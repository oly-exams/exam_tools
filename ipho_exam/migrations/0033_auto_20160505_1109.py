# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0032_auto_20160427_2319'),
    ]

    operations = [
        migrations.AddField(
            model_name='examdelegationsubmission',
            name='action',
            field=models.CharField(default='T', max_length=2, choices=[(b'T', b'Translation submission'), (b'P', b'Points submission')]),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='examdelegationsubmission',
            unique_together=set([('exam', 'delegation', 'action')]),
        ),
    ]
