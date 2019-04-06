# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ipho_exam.models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0067_document_scan_file_orig'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='scan_file_orig',
            field=models.FileField(upload_to=ipho_exam.models.exam_scans_orig_filename, blank=True),
        ),
    ]
