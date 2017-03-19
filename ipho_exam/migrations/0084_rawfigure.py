# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0083_figure_polymorphic_ctype'),
    ]

    operations = [
        migrations.CreateModel(
            name='RawFigure',
            fields=[
                ('figure_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='ipho_exam.Figure')),
                ('content', models.BinaryField()),
                ('filetype', models.CharField(max_length=4)),
            ],
            options={
                'abstract': False,
            },
            bases=('ipho_exam.figure',),
        ),
    ]
