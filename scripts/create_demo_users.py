import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'iphoadmin.settings'

import django
django.setup()

import csv
from ipho_core.models import Delegation, Student, User, Group, AutoLogin


def main(input):
    reader = csv.DictReader(input)
    
    delegations_group = Group.objects.get(name='Delegation')
    for i,row in enumerate(reader):
        delegation = Delegation.objects.get(name=row['Country code'])
        
        
        user = User(username=row['Country code'], first_name=row['Country name'])
        try:
            db_user = User.objects.get(username=row['Country code'])
            user.pk = db_user.pk
        except User.DoesNotExist:
            pass
        user.set_password(row['Password'])
        user.save()
        
        user.groups.add(delegations_group)
        user.save()
        
        delegation.members.add(user)
        delegation.save()
        
        autologin = AutoLogin(user=user)
        autologin.save()
        
        print row['Country code'], '...', 'imported.'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import CSV to users and assign delegations')
    parser.add_argument('file', type=argparse.FileType('rU'), help='Input CSV file')
    args = parser.parse_args()
    
    main(args.file)

