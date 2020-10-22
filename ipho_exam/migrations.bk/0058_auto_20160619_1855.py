from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0057_auto_20160619_1739"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="exam",
            name="feedback_active",
        ),
        migrations.AddField(
            model_name="question",
            name="feedback_active",
            field=models.BooleanField(
                default=False, help_text=b"Are feedbacks allowed?"
            ),
        ),
    ]
