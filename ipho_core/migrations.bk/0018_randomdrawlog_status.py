from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0017_randomdrawlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="randomdrawlog",
            name="status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("received", "Received")],
                default="pending",
                max_length=200,
            ),
        ),
    ]
