from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0042_step2"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="question",
            options={"ordering": ["position", "type"]},
        ),
    ]
