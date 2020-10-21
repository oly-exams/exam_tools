from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0058_auto_20160619_1855"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feedback",
            name="part",
            field=models.CharField(default=None, max_length=100),
        ),
    ]
