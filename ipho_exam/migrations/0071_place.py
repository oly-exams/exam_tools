# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0009_auto_20160626_1205'),
        ('ipho_exam', '0070_auto_20160706_1727'),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('exam', models.ForeignKey(to='ipho_exam.Exam')),
                ('student', models.ForeignKey(to='ipho_core.Student')),
            ],
        ),
    ]
