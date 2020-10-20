from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_poll", "0002_auto_20160613_1653"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="implementation",
            field=models.PositiveSmallIntegerField(
                default=0, choices=[(0, b"Not implemented"), (1, b"Implemented")]
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="vote_result",
            field=models.PositiveSmallIntegerField(
                default=0,
                choices=[(0, b"In progress"), (1, b"Rejected"), (2, b"Accepted")],
            ),
        ),
    ]
