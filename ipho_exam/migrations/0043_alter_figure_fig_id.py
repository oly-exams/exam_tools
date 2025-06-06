# Generated by Django 4.1.12 on 2024-07-06 10:51

from django.db import migrations, models

import ipho_exam.utils.natural_id


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0042_feedback_sort_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='figure',
            name='fig_id',
            field=models.CharField(db_index=True, default=ipho_exam.utils.natural_id.generate_id, max_length=100, unique=True),
        ),
    ]
