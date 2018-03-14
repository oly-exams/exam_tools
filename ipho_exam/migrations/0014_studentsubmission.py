# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0005_iphoperm'),
        ('ipho_exam', '0013_auto_20151107_1041'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('exam', models.ForeignKey(to='ipho_exam.Exam')),
                ('language', models.ForeignKey(to='ipho_exam.Language')),
                ('student', models.ForeignKey(to='ipho_core.Student')),
            ],
            options={},
            bases=(models.Model, ),
        ),
    ]
