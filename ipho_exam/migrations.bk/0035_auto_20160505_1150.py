# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0034_rename_examdelegation_submission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examaction',
            name='delegation',
            field=models.ForeignKey(related_name='exam_status', to='ipho_core.Delegation'),
        ),
        migrations.AlterField(
            model_name='examaction',
            name='exam',
            field=models.ForeignKey(related_name='delegation_status', to='ipho_exam.Exam'),
        ),
    ]
