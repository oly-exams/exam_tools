# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ipho_exam.models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0038_auto_20160523_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='file',
            field=models.FileField(upload_to=ipho_exam.models.exam_prints_filename, blank=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='scan_file',
            field=models.FileField(upload_to=ipho_exam.models.exam_scans_filename, blank=True),
        ),
    ]
