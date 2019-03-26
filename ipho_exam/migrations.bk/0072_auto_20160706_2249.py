# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0071_place'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('student', 'exam')]),
        ),
        migrations.AlterIndexTogether(
            name='place',
            index_together=set([('student', 'exam')]),
        ),
    ]
