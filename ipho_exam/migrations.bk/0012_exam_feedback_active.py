from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0011_auto_20151006_2328"),
    ]

    operations = [
        migrations.AddField(
            model_name="exam",
            name="feedback_active",
            field=models.BooleanField(
                default=False, help_text=b"Are feedbacks allowed?"
            ),
            preserve_default=True,
        ),
    ]
