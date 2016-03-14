import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

import csv
from ipho_core.models import Delegation, Student

def main(input):
    reader = csv.DictReader(input)
    
    for i,row in enumerate(reader):
        delegation = Delegation(name=row['Country code'], country=row['Country name'])
        nk = delegation.natural_key()
        try:
            current_delegation = Delegation.objects.get_by_natural_key(*nk)
            print row['Country code'], '...', 'already present. Skip.'
            continue
        except Delegation.DoesNotExist:
            pass
        delegation.save()
        
        for j in range(5):
            code = '{}-S-{}'.format(delegation.name, j+1)
            student = Student(code=code, first_name='Student', last_name=str(j+1), delegation=delegation)
            student.save()
        
        print row['Country code'], '...', 'imported.'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import CSV to Delegation model and create demo students')
    parser.add_argument('file', type=argparse.FileType('rU'), help='Input CSV file')
    args = parser.parse_args()
    
    main(args.file)

