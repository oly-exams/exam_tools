# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0023_auto_20160207_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='font',
            field=models.CharField(default=b'Arial Unicode MS', max_length=100, choices=[(b'Arial Unicode MS', b'Arial'), (b'Amiri', b'Amiri')]),
        ),
    ]
