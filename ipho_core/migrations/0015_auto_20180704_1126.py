# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0014_accountrequest'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='iphoperm',
            options={'permissions': (('is_delegation', 'Is a delegation'), ('is_marker', 'Is a marker'), ('can_vote', 'Can vote'), ('is_staff', 'Is an organizer'), ('can_impersonate', 'Can impersonate delegations'), ('print_technopark', 'Can print in Technopark'), ('print_irchel', 'Can print in Irchel'), ('is_printstaff', 'Is a print staff'))},
        ),
    ]
