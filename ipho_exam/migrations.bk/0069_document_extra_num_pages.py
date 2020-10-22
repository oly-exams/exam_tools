from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0068_auto_20160703_0941"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="extra_num_pages",
            field=models.IntegerField(default=0),
        ),
    ]
