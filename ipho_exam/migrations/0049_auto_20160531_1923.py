# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Question = apps.get_model("ipho_exam", "Question")
    for q in Question.objects.using(db_alias).all():
	if q.type == 0:
		q.code = 'Q'
	elif q.type == 1:
		q.code = 'A'
        q.save()

def backwards_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0048_auto_20160531_1921'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
