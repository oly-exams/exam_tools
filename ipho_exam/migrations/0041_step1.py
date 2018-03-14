# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def forwards_func(apps, schema_editor):
    Question = apps.get_model("ipho_exam", "Question")
    db_alias = schema_editor.connection.alias
    for q in Question.objects.using(db_alias).all():
    if q.type == 'Q': q.type_num = 0
    if q.type == 'A': q.type_num = 1
    q.save()

def backwards_func(apps, schema_editor):
    Question = apps.get_model("ipho_exam", "Question")
    db_alias = schema_editor.connection.alias
    for q in Question.objects.using(db_alias).all():
    if q.type_num == 0: q.type = 'Q'
    if q.type_num == 1: q.type = 'A'
    q.save()

class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0040_question_type_num'),
    ]

    operations = [
        migrations.RunPython(forwards_func,backwards_func),
    ]
