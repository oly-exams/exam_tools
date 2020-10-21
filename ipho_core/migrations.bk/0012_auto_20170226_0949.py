from django.conf import settings
from django.db import migrations, models


def change_official(apps, schema_editor):  # pylint: disable=unused-argument
    delegation = apps.get_model("ipho_core", "Delegation")
    try:
        official_delegation = delegation.objects.get(name="IPhO")
        official_delegation.name = settings.OFFICIAL_DELEGATION
        official_delegation.save()
    except delegation.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0011_auto_20170226_0947"),
    ]

    operations = [migrations.RunPython(change_official)]
