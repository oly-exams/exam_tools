import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exam_tools.settings")
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

import argparse

import django

django.setup()

from ipho_exam import qml
from ipho_exam.models import Exam, Question, VersionNode


# based admin_publish_version(request, exam_id, question_id, version_num) publish all versions from the questions of an exam
def publish_all_questions(exam_id):
    exam = Exam.objects.get(pk=exam_id)
    questions = Question.objects.filter(exam=exam)
    for question in questions:
        versions = VersionNode.objects.filter(question=question)
        for version in versions:
            node = version
            node.status = "C"
            # Save the ids in order, so they can be used for feedback sorting
            qmln = qml.make_qml(node)
            ids_in_order = []

            def get_ids(obj):
                if obj.id is not None:
                    ids_in_order.append(obj.id)
                for child in obj.children:
                    get_ids(child)

            get_ids(qmln)
            node.ids_in_order = ",".join(ids_in_order)
            node.save()

        exam_id = node.question.exam.id
    return questions.count()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exam_name", help="Name of the exam to publish")
    parser.add_argument("--all_exams", action="store_true", help="Publish all exams")
    args = parser.parse_args()
    if args.all_exams:
        exam_names = Exam.objects.values_list("name", flat=True)
        for exam_name in exam_names:
            exam_id = Exam.objects.get(name=exam_name).pk
            num_questions = publish_all_questions(exam_id)
            print(
                f"Published all versions for {num_questions} questions from exam {exam_name}"
            )
    else:
        exam_name = args.exam_name
        exam_id = Exam.objects.get(name=exam_name).pk
        num_questions = publish_all_questions(exam_id)
        print(
            f"Published all versions for {num_questions} questions from exam {exam_name}"
        )
