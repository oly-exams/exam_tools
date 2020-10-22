from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0002_auto_20150222_1914"),
    ]

    operations = [
        migrations.AlterField(
            model_name="language",
            name="delegation",
            field=models.ManyToManyField(to="ipho_core.Delegation", blank=True),
            preserve_default=True,
        ),
    ]
