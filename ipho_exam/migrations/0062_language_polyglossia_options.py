# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0061_question_working_pages'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='polyglossia_options',
            field=models.TextField(null=True, blank=True),
        ),
    ]
