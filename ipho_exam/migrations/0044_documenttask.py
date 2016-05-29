# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0043_auto_20160528_1544'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_id', models.CharField(unique=True, max_length=255)),
                ('document', models.ForeignKey(to='ipho_exam.Document')),
            ],
        ),
    ]
