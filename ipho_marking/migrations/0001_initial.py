# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0030_language_style'),
    ]

    operations = [
        migrations.CreateModel(
            name='Marking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('points', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='QuestionPoints',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.ForeignKey(to='ipho_exam.Question')),
            ],
        ),
        migrations.AddField(
            model_name='marking',
            name='question_points',
            field=models.ForeignKey(to='ipho_marking.QuestionPoints'),
        ),
    ]
