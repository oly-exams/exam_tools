from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0019_auto_20180725_0306"),
    ]

    operations = [
        migrations.AddField(
            model_name="randomdrawlog",
            name="tag",
            field=models.CharField(default="", max_length=200),
        ),
    ]
