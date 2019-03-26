# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0005_iphoperm'),
        ('ipho_exam', '0014_studentsubmission'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamDelegationSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (
                    'status',
                    models.CharField(
                        default=b'O', max_length=1, choices=[(b'O', b'In progress'), (b'S', b'Submitted')]
                    )
                ),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('delegation', models.ForeignKey(to='ipho_core.Delegation')),
                ('exam', models.ForeignKey(to='ipho_exam.Exam')),
            ],
            options={},
            bases=(models.Model, ),
        ),
    ]
