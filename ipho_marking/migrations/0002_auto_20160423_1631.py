# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0030_language_style'),
        ('ipho_marking', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarkingMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=2)),
                ('max_points', models.FloatField()),
                ('position', models.PositiveSmallIntegerField(help_text=b'Sorting index inside one question')),
                ('question', models.ForeignKey(to='ipho_exam.Question')),
            ],
        ),
        migrations.RemoveField(
            model_name='questionpoints',
            name='question',
        ),
        migrations.AlterField(
            model_name='marking',
            name='question_points',
            field=models.ForeignKey(to='ipho_marking.MarkingMeta'),
        ),
        migrations.DeleteModel(
            name='QuestionPoints',
        ),
    ]
