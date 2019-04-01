# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_marking', '0006_auto_20160430_1450'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='markingmeta',
            index_together=set([('question', 'name')]),
        ),
    ]
