# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def copy_delegation(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Language = apps.get_model("ipho_exam", "Language")
    for lang in Language.objects.all():
        for deleg in lang.delegation.all():
            lang.delegation2 = deleg
            lang.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_core', '0004_auto_20150222_2105'),
        ('ipho_exam', '0006_language_delegation2'),
    ]

    operations = [
        migrations.RunPython(copy_delegation),
    ]
