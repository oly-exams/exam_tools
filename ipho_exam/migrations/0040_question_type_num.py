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
        ('ipho_exam', '0039_auto_20160524_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='type_num',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'Question'), (1, b'Answer')]),
        ),
        migrations.RunPython(forwards_func,backwards_func),
        migrations.RemoveField(
            model_name='question',
            name='type',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='type_num',
            new_name='type',
        ),
    ]
