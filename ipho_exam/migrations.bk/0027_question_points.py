from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0026_auto_20160229_2149"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="points",
            field=models.PositiveSmallIntegerField(default=20),
        ),
    ]
