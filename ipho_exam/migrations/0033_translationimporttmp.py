# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0032_auto_20160427_2319'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranslationImportTmp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)),
                ('content', models.TextField(blank=True)),
                ('language', models.ForeignKey(to='ipho_exam.Language')),
                ('question', models.ForeignKey(to='ipho_exam.Question')),
            ],
        ),
    ]
