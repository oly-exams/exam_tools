# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0008_auto_20160528_1544'),
        ('ipho_exam', '0051_auto_20160612_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'N', max_length=1, choices=[(b'N', b'None'), (b'L', b'Liked'), (b'U', b'Unliked')])),
                ('Feedback', models.ForeignKey(to='ipho_exam.Feedback')),
                ('delegation', models.ForeignKey(to='ipho_core.Delegation')),
            ],
        ),
    ]
