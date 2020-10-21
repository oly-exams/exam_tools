from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0015_examdelegationsubmission"),
    ]

    operations = [
        migrations.AlterField(
            model_name="examdelegationsubmission",
            name="status",
            field=models.CharField(
                default=b"O",
                max_length=1,
                choices=[
                    (b"O", b"In progress"),
                    (b"S", b"Translations submitted"),
                    (b"A", b"Translations assigned"),
                ],
            ),
            preserve_default=True,
        ),
    ]
