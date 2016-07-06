import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

import csv
from ipho_core.models import Student
from ipho_exam.models import Place, Exam

def main(input):
    reader = csv.DictReader(input)

    theory = Exam.objects.get(name='Theory')
    experiment = Exam.objects.get(name='Experiment')
    for i,row in enumerate(reader):
        try:
            student = Student.objects.get(code=row['individual_id'])

            Place(student=student, exam=theory, name=row['seat_theory']).save()
            Place(student=student, exam=experiment, name=row['seat_experiment']).save()

            print row['individual_id'], '.....', 'imported.'
        except Delegation.DoesNotExist:
            print 'Skip', row['individual_id'], 'because delegation does not exist.'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import CSV with users seating info')
    parser.add_argument('file', type=argparse.FileType('rU'), help='Input CSV file')
    args = parser.parse_args()

    main(args.file)
