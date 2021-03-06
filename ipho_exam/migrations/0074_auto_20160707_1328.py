# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0073_auto_20160707_1010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='status',
            field=models.CharField(
                default=b'S',
                max_length=1,
                choices=[(b'S', b'Submitted'), (b'V', b'Schedule for voting'), (b'I', b'Implemented'),
                         (b'T', b'Settle')]
            ),
        ),
    ]
