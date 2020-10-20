from django.db import migrations, models


def forwards_func(apps, schema_editor):
    Exam = apps.get_model("ipho_exam", "Exam")
    ExamAction = apps.get_model("ipho_exam", "ExamAction")
    Delegation = apps.get_model("ipho_core", "Delegation")
    db_alias = schema_editor.connection.alias
    for delegation in Delegation.objects.using(db_alias).all():
        for exam in Exam.objects.using(db_alias).all():
            for action in [
                "T",
                "P",
            ]:  # would be nicer to have ExamAction.ACTION_CHOICES, but it is not accessible
                exam_action, _ = ExamAction.objects.using(db_alias).get_or_create(
                    exam=exam, delegation=delegation, action=action
                )


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0035_auto_20160505_1150"),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
