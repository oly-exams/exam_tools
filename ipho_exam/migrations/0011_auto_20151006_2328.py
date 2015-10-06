# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0005_iphoperm'),
        ('ipho_exam', '0010_auto_20150514_2346'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(blank=True)),
                ('status', models.CharField(default=b'O', max_length=1, choices=[(b'O', b'In progress'), (b'A', b'Accepted'), (b'R', b'Rejected')])),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('delegation', models.ForeignKey(to='ipho_core.Delegation')),
                ('question', models.ForeignKey(to='ipho_exam.Question')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='translationnode',
            name='status',
            field=models.CharField(default=b'O', max_length=1, choices=[(b'O', b'In progress'), (b'L', b'Locked'), (b'S', b'Submitted')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='translationnode',
            name='text',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='versionnode',
            name='status',
            field=models.CharField(max_length=1, choices=[(b'P', b'Proposal'), (b'C', b'Confirmed')]),
            preserve_default=True,
        ),
    ]
