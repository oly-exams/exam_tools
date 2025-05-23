# Generated by Django 3.2.13 on 2022-06-27 16:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0029_feedback_part_position"),
        ("ipho_marking", "0004_alter_marking_points"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuestionPointsRescale",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "max_internal_points",
                    models.DecimalField(decimal_places=2, max_digits=8),
                ),
                (
                    "max_external_points",
                    models.DecimalField(decimal_places=2, max_digits=8),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ipho_exam.question",
                    ),
                ),
            ],
            options={
                "ordering": ["question"],
                "unique_together": {("question",)},
                "index_together": {("question",)},
            },
        ),
    ]
