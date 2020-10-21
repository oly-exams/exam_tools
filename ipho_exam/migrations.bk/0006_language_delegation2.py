from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0004_auto_20150222_2105"),
        ("ipho_exam", "0005_auto_20150509_2109"),
    ]

    operations = [
        migrations.AddField(
            model_name="language",
            name="delegation2",
            field=models.ForeignKey(
                related_name="lang_delegation",
                blank=True,
                to="ipho_core.Delegation",
                null=True,
            ),
            preserve_default=True,
        ),
    ]
