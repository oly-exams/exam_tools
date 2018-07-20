# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0016_pushsubscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='RandomDrawLog',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('delegation', models.ForeignKey(to='ipho_core.Delegation')),
            ],
        ),
    ]
