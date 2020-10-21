from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0094_document_timestamp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feedback",
            name="status",
            field=models.CharField(
                choices=[
                    ("S", "Submitted"),
                    ("V", "Scheduled for voting"),
                    ("I", "Implemented"),
                    ("T", "Settled"),
                    ("R", "Rejected"),
                ],
                default="S",
                max_length=1,
            ),
        ),
    ]
