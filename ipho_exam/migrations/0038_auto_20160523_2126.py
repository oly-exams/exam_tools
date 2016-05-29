# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0007_autologin'),
        ('ipho_exam', '0037_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField()),
                ('file', models.FileField(upload_to=b'', blank=True)),
                ('num_pages', models.IntegerField(default=0)),
                ('barcode_num_pages', models.IntegerField(default=0)),
                ('barcode_base', models.CharField(max_length=20)),
                ('scan_file', models.FileField(upload_to=b'', blank=True)),
                ('exam', models.ForeignKey(to='ipho_exam.Exam')),
                ('student', models.ForeignKey(to='ipho_core.Student')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together=set([('exam', 'student', 'position')]),
        ),
    ]
