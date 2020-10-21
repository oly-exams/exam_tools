from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0062_language_polyglossia_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="barcode_base",
            field=models.TextField(),
        ),
    ]
