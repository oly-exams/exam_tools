# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0063_auto_20160623_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='figure',
            name='name',
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='name',
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterIndexTogether(
            name='document',
            index_together=set([('exam', 'student', 'position')]),
        ),
        migrations.AlterIndexTogether(
            name='examaction',
            index_together=set([('exam', 'delegation', 'action')]),
        ),
        migrations.AlterIndexTogether(
            name='language',
            index_together=set([('name', 'delegation')]),
        ),
        migrations.AlterIndexTogether(
            name='like',
            index_together=set([('delegation', 'feedback')]),
        ),
        migrations.AlterIndexTogether(
            name='pdfnode',
            index_together=set([('question', 'language')]),
        ),
        migrations.AlterIndexTogether(
            name='studentsubmission',
            index_together=set([('student', 'exam', 'language')]),
        ),
        migrations.AlterIndexTogether(
            name='translationnode',
            index_together=set([('question', 'language')]),
        ),
        migrations.AlterIndexTogether(
            name='versionnode',
            index_together=set([('question', 'language', 'version')]),
        ),
    ]
