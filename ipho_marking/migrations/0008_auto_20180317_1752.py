# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_marking', '0007_auto_20160623_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marking',
            name='version',
            field=models.CharField(max_length=1, choices=[('O', 'Organizers'), ('D', 'Delegation'), ('F', 'Final')]),
        ),
        migrations.AlterField(
            model_name='markingmeta',
            name='position',
            field=models.PositiveSmallIntegerField(default=10, help_text='Sorting index inside one question'),
        ),
    ]
