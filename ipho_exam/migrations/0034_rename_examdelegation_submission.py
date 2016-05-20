# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0033_auto_20160505_1109'),
    ]

    operations = [
        migrations.RenameModel('ExamDelegationSubmission', 'ExamAction')
    ]
