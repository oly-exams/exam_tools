from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0039_auto_20160524_2155"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="type_num",
            field=models.PositiveSmallIntegerField(
                default=0, choices=[(0, b"Question"), (1, b"Answer")]
            ),
        ),
    ]
