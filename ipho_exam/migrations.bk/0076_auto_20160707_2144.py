# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0075_auto_20160707_1411'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(blank=True)),
                ('language', models.ForeignKey(to='ipho_exam.Language')),
                ('node', models.ForeignKey(to='ipho_exam.TranslationNode')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='attributechange',
            unique_together=set([('node', 'language')]),
        ),
        migrations.AlterIndexTogether(
            name='attributechange',
            index_together=set([('node', 'language')]),
        ),
    ]
