from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0045_auto_20160529_1458"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedback",
            name="part",
            field=models.CharField(default="General", max_length=100),
            preserve_default=False,
        ),
    ]
