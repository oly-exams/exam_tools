# Generated by Django 3.1.3 on 2020-11-05 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0006_auto_20201105_1037"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exam",
            name="moderation",
            field=models.IntegerField(
                choices=[(-1, "Not open"), (0, "Can be moderated")],
                default=-1,
                help_text="Allow access to moderation interface.",
                verbose_name="Moderation",
            ),
        ),
    ]
