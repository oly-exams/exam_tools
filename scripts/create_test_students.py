import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'iphoadmin.settings'

import django
django.setup()

import csv
from ipho_core.models import Delegation, Student

def main(input):
    csv_reader = csv.reader(input)
    
    all_delegations = Delegation.objects.all()
    for i,row in enumerate(csv_reader):
        delegation = all_delegations[i / 5]
        
        code = '{}-S-{}'.format(delegation.name, i%5+1)
        student = Student(code=code, first_name=row[2], last_name=row[3], delegation=delegation)
        student.save()
        
        if (i+1)/5 >= len(all_delegations):
            break

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert CSV to Delegation fixture')
    parser.add_argument('file', type=argparse.FileType('rU'), help='Input CSV file')
    args = parser.parse_args()
    
    main(args.file)
