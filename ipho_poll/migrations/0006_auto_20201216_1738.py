# Generated by Django 3.1.3 on 2020-12-16 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0015_auto_20201119_1911"),
        ("ipho_poll", "0005_auto_20201216_1110"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Question",
            new_name="Voting",
        ),
        migrations.RenameField(
            model_name="choice",
            old_name="question",
            new_name="voting",
        ),
        migrations.RenameField(
            model_name="vote",
            old_name="question",
            new_name="voting",
        ),
        migrations.AlterUniqueTogether(
            name="vote",
            unique_together={("voting", "voting_right")},
        ),
    ]
