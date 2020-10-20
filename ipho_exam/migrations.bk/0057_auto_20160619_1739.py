from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0056_versionnode_tag"),
    ]

    operations = [
        migrations.AlterField(
            model_name="versionnode",
            name="status",
            field=models.CharField(
                max_length=1,
                choices=[(b"P", b"Proposal"), (b"S", b"Staged"), (b"C", b"Confirmed")],
            ),
        ),
    ]
