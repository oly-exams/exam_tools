# Generated by Django 4.1.13 on 2025-04-06 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0044_merge_20250406_1454"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="question",
            options={"ordering": ["exam", "position", "type", "code"]},
        ),
        migrations.AlterField(
            model_name="question",
            name="code",
            field=models.CharField(
                choices=[
                    ("Q", "Q (Question)"),
                    ("A", "A (Answer)"),
                    ("G", "G (General)"),
                ],
                default="Q",
                max_length=20,
            ),
        ),
    ]
