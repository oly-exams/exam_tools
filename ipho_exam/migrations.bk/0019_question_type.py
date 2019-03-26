# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0018_auto_20151115_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='type',
            field=models.CharField(default=b'Q', max_length=1, choices=[(b'Q', b'Question'), (b'A', b'Answer')]),
        ),
    ]
