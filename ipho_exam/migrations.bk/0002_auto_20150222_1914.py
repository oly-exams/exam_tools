from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="translationnode",
            unique_together={("question", "language")},
        ),
        migrations.AlterUniqueTogether(
            name="versionnode",
            unique_together={("question", "language", "version")},
        ),
    ]
