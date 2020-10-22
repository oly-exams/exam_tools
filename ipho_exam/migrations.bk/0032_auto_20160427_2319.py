from django.db import migrations, models
import ipho_exam.models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0031_auto_20160425_1752"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pdfnode",
            name="pdf",
            field=models.FileField(
                upload_to=ipho_exam.models.get_file_path, blank=True
            ),
        ),
    ]
