# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0059_auto_20160620_2023'),
        ('ipho_poll', '0003_auto_20160618_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='feedbacks',
            field=models.ManyToManyField(related_name='vote', to='ipho_exam.Feedback', blank=True),
        ),
    ]
