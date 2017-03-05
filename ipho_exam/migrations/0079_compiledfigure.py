# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0078_auto_20170218_1212'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompiledFigure',
            fields=[
                ('figure_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='ipho_exam.Figure')),
            ],
            bases=('ipho_exam.figure',),
        ),
    ]
