# Generated by Django 3.1.3 on 2021-02-20 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0006_auto_20201123_2133"),
        ("ipho_exam", "0018_auto_20210220_1633"),
    ]

    operations = [
        migrations.AddField(
            model_name="participant",
            name="students",
            field=models.ManyToManyField(to="ipho_core.Student"),
        ),
    ]
