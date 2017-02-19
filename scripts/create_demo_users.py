# Exam Tools
#    
# Copyright (C) 2014 - 2017 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

import csv
from ipho_core.models import Delegation, Student, User, Group, AutoLogin


def main(input, autologins):
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
        
        if autologins:
            autologin = AutoLogin(user=user)
            autologin.save()
        
        print row['Country code'], '...', 'imported.'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import CSV to users and assign delegations')
    parser.add_argument('file', type=argparse.FileType('rU'), help='Input CSV file')
    parser.add_argument('--without_autologings',  dest='autologins', action='store_false', help='Discard autologin')
    args = parser.parse_args()
    
    main(args.file, args.autologins)

