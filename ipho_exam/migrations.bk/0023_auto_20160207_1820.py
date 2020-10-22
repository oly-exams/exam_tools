from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0022_language_direction"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exam",
            name="name",
            field=models.CharField(unique=True, max_length=100),
        ),
    ]
