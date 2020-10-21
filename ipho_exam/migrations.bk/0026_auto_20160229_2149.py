from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0025_auto_20160228_1738"),
    ]

    operations = [
        migrations.AlterField(
            model_name="language",
            name="name",
            field=models.CharField(max_length=100),
        ),
    ]
