# Generated by Django 3.1.3 on 2021-02-20 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0016_auto_20210218_1233"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="participant",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="participant",
            name="last_name",
        ),
        migrations.AddField(
            model_name="participant",
            name="full_name",
            field=models.CharField(default="", max_length=400),
            preserve_default=False,
        ),
    ]
