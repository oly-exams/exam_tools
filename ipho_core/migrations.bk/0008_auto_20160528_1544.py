from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0007_autologin"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="iphoperm",
            options={
                "permissions": (
                    ("is_leader", "Is a leader"),
                    ("is_staff", "Is an organizer"),
                    ("print_technopark", "Can print in Technopark"),
                    ("print_irchel", "Can print in Irchel"),
                )
            },
        ),
    ]
