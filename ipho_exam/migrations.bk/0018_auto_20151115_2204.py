from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0017_auto_20151109_2225"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentsubmission",
            name="with_answer",
            field=models.BooleanField(
                default=False, help_text=b"Deliver also answer sheet."
            ),
        ),
        migrations.AlterField(
            model_name="examdelegationsubmission",
            name="status",
            field=models.CharField(
                default=b"O",
                max_length=1,
                choices=[(b"O", b"In progress"), (b"S", b"Submitted")],
            ),
        ),
    ]
