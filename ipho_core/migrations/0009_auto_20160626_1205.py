# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0008_auto_20160528_1544'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='iphoperm',
            options={
                'permissions':
                (('is_delegation', 'Is a delegation'), ('is_marker', 'Is a marker'), ('can_vote', 'Can vote'),
                 ('is_staff', 'Is an organizer'), ('print_technopark',
                                                   'Can print in Technopark'), ('print_irchel', 'Can print in Irchel'))
            },
        ),
    ]
