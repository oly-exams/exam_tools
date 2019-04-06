# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0044_documenttask'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documenttask',
            name='document',
            field=models.OneToOneField(to='ipho_exam.Document'),
        ),
    ]
