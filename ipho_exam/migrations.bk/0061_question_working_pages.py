from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0060_auto_20160622_1351"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="working_pages",
            field=models.PositiveSmallIntegerField(
                default=0, help_text=b"How many pages for working sheets"
            ),
        ),
    ]
