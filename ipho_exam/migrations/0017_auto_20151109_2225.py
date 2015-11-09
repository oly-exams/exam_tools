# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0016_auto_20151109_1835'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='examdelegationsubmission',
            unique_together=set([('exam', 'delegation')]),
        ),
        migrations.AlterUniqueTogether(
            name='studentsubmission',
            unique_together=set([('student', 'exam', 'language')]),
        ),
    ]
