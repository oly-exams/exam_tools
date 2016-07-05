import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

import csv
from ipho_core.models import Delegation, Student, Group, User, AutoLogin
from ipho_poll.models import VotingRight


def main(input):
    reader = csv.DictReader(input)
    
    
    delegations_group = Group.objects.get(name='Delegation')
    for i,row in enumerate(reader):
        ## Delegation
        delegation,created = Delegation.objects.get_or_create(name=row['Country Code'], defaults={'country':row['Country Name']})
        if created: print delegation, '..', 'created'
        
        ## User
        user,created = User.objects.get_or_create(username=row['Country Code'])
        user.set_password(row['Password'])
        user.groups.add(delegations_group)
        user.save()
        if created: print user, '..', 'created'
        
        if not hasattr(user, 'autologin'):
            autologin = AutoLogin(user=user)
            autologin.save()
            print 'Autologin created'
        
        delegation.members.add(user)
        delegation.save()
        
        ## VotingRights
        for j in range(int(row['Leaders'])):
            if j == 0:
                name = 'A'
            elif j == 1:
                name = 'B'
            else:
                print 'Nobody should have three voting rights!'
                continue
            vt,created = VotingRight.objects.get_or_create(user=user, name='Leader '+name)
            if created: print vt, '..', 'created'
        
        print row['Country Code'], '...', 'imported.'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import CSV Delegation data')
    parser.add_argument('file', type=argparse.FileType('rU'), help='Input CSV file')
    args = parser.parse_args()
    
    main(args.file)

