# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0009_rename_delegation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Figure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('content', models.TextField(blank=True)),
                ('params', models.TextField(blank=True)),
            ],
            options={},
            bases=(models.Model, ),
        ),
        migrations.AlterField(
            model_name='language',
            name='delegation',
            field=models.ForeignKey(blank=True, to='ipho_core.Delegation', null=True),
            preserve_default=True,
        ),
    ]
