import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

import csv
from django.contrib.auth.models import Permission
from ipho_core.models import Group, User
from ipho_poll.models import VotingRight


def main(input):
    reader = csv.DictReader(input)

    can_vote = Permission.objects.get(name='Can vote')
    for i,row in enumerate(reader):
        group = None
        if row['Group'] != '':
            group = Group.objects.get(name=row['Group'])

        is_admin = (row['Group'] == 'Admin')
        is_super = (row['Superuser'] == 'yes')

        ## User
        user,created = User.objects.get_or_create(username=row['Username'], defaults={
            'first_name': row['First name'],
            'last_name': row['Last name'],
            'is_staff': is_super,
            'is_superuser': is_super,
        })
        user.set_password(row['Password'])
        if group is not None:
            user.groups.add(group)
        user.save()
        if created: print user, '..', 'created'

        ## VotingRights
        votingrights = int(int(row['VotingRight']))
        if votingrights > 0:
            user.user_permissions.add(can_vote)
        for j in range(votingrights):
            vt,created = VotingRight.objects.get_or_create(user=user, name=u'{} {}'.format(user.first_name, user.last_name))
            if created: print vt, '..', 'created'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import CSV to User model')
    parser.add_argument('file', type=argparse.FileType('rU'), help='Input CSV file')
    args = parser.parse_args()

    main(args.file)
