# Generated by Django 3.1.3 on 2020-11-05 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0005_auto_20201104_1526"),
    ]

    operations = [
        migrations.AddField(
            model_name="exam",
            name="moderation",
            field=models.IntegerField(
                choices=[
                    (-1, "Not open"),
                    (0, "Organizer only"),
                    (1, "Organizer done, delegation can submit"),
                ],
                default=-1,
                help_text="Allow access to moderation interface.",
                verbose_name="Moderation",
            ),
        ),
        migrations.AlterField(
            model_name="exam",
            name="marking",
            field=models.IntegerField(
                choices=[
                    (-1, "Not open"),
                    (0, "Organizer only"),
                    (1, "Organizer done, delegation can submit"),
                ],
                default=-1,
                help_text="Sets the ability to enter marks for organizers and delegations.",
                verbose_name="Marking",
            ),
        ),
    ]
