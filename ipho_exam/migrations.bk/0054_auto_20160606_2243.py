from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0053_auto_20160605_1133"),
    ]

    operations = [
        migrations.AlterField(
            model_name="like",
            name="status",
            field=models.CharField(
                max_length=1, choices=[(b"L", b"Liked"), (b"U", b"Unliked")]
            ),
        ),
        migrations.AlterUniqueTogether(
            name="like",
            unique_together={("delegation", "feedback")},
        ),
    ]
