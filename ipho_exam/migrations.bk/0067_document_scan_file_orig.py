from django.db import migrations, models
import ipho_exam.models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0066_exam_marking_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="scan_file_orig",
            field=models.FileField(
                upload_to=ipho_exam.models.exam_scans_filename, blank=True
            ),
        ),
    ]
