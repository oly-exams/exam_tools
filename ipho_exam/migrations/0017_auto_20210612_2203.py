# Generated by Django 3.1.4 on 2021-06-12 20:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0016_alter_language_polyglossia"),
    ]

    operations = [
        migrations.RenameField(
            model_name="printlog",
            old_name="type",
            new_name="doctype",
        ),
    ]
