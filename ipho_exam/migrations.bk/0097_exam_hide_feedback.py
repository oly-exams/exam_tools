from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0096_auto_20180724_1310"),
    ]

    operations = [
        migrations.AddField(
            model_name="exam",
            name="hide_feedback",
            field=models.BooleanField(
                default=False, help_text="Hide feedback from delegations"
            ),
        ),
    ]
