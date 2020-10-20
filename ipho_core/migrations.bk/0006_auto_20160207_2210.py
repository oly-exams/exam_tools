from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0005_iphoperm"),
    ]

    operations = [
        migrations.AlterField(
            model_name="delegation",
            name="name",
            field=models.CharField(unique=True, max_length=4),
        ),
    ]
