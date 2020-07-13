# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
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

from builtins import str
from builtins import range
import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

from django.core import serializers
import csv

from ipho_core.models import Delegation, Student, Group, User
from ipho_poll.models import VotingRight


def log(*args):
    sys.stderr.write(' '.join([str(a) for a in args]) + '\n')


def create_objs(input):
    reader = csv.DictReader(input)

    created_objs = []
    delegations_examsite_group = Group.objects.get(name='Delegation Examsite Team')
    for i, row in enumerate(reader):
        ## Delegation
        delegation = Delegation.objects.get(name=row['Country Code'])

        ## User
        username = '{}-Examsite'.format(row['Country Code'])
        user, created = User.objects.get_or_create(username=username)
        user.set_password(row['Password'])
        user.groups.add(delegations_examsite_group)
        user.save()
        if created: log(user, '..', 'created')
        created_objs.append(user)

        delegation.members.add(user)
        delegation.save()
        created_objs.append(delegation)

        log(username, '...', 'imported.')
    return created_objs


def main(input, dumpdata=False):
    created_objs = create_objs(input)

    if dumpdata:
        serializers.serialize(
            'json',
            created_objs,
            indent=2,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True,
            stream=sys.stdout
        )


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import CSV Delegation data')
    parser.add_argument('--dumpdata', action='store_true', help='Dump Json data')
    parser.add_argument('file', type=argparse.FileType('rU'), help='Input CSV file')
    args = parser.parse_args()

    main(args.file, args.dumpdata)
