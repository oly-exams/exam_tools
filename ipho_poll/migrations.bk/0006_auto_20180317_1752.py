from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_poll", "0005_auto_20160708_2224"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="end_date",
            field=models.DateTimeField(verbose_name="end date", blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="question",
            name="implementation",
            field=models.PositiveSmallIntegerField(
                default=0, choices=[(0, "Not implemented"), (1, "Implemented")]
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="pub_date",
            field=models.DateTimeField(
                verbose_name="date published", default=django.utils.timezone.now
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="vote_result",
            field=models.PositiveSmallIntegerField(
                default=0,
                choices=[(0, "In progress"), (1, "Rejected"), (2, "Accepted")],
            ),
        ),
    ]
