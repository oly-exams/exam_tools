# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
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

import os, sys

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import django

django.setup()

from django.core import serializers
import csv

from ipho_core.models import Delegation, Group, User, AutoLogin
from ipho_poll.models import VotingRight


def log(*args):
    sys.stderr.write(" ".join([str(a) for a in args]) + "\n")


def create_objs(input):
    reader = csv.DictReader(input)

    created_objs = []
    delegations_group = Group.objects.get(name="Delegation")
    for i, row in enumerate(reader):

        ## Delegation
        delegation, created = Delegation.objects.get_or_create(
            name=row["Country Code"], defaults={"country": row["Country Name"]}
        )
        if created:
            log(delegation, "..", "created")

        ## User
        user, created = User.objects.get_or_create(username=row["Country Code"])
        user.set_password(row["Password"])
        user.groups.add(delegations_group)
        user.save()
        if created:
            log(user, "..", "created")
        created_objs.append(user)

        if not hasattr(user, "autologin"):
            autologin = AutoLogin(user=user)
            autologin.save()
            log("Autologin created")
        created_objs.append(user.autologin)

        delegation.members.add(user)
        delegation.save()
        created_objs.append(delegation)

        ## VotingRights
        for j in range(int(row["Leaders"])):
            if j == 0:
                name = "A"
            elif j == 1:
                name = "B"
            else:
                log("Nobody should have three voting rights!")
                continue
            vt, created = VotingRight.objects.get_or_create(
                user=user, name="Leader " + name
            )
            if created:
                log(vt, "..", "created")
            created_objs.append(vt)

        log(row["Country Code"], "...", "imported.")
    return created_objs


def main(input, dumpdata=False):
    created_objs = create_objs(input)

    if dumpdata:
        serializers.serialize(
            "json",
            created_objs,
            indent=2,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True,
            stream=sys.stdout,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import CSV Delegation data")
    parser.add_argument("--dumpdata", action="store_true", help="Dump Json data")
    parser.add_argument(
        "file",
        type=argparse.FileType("rU", encoding="utf-8-sig"),
        help="Input CSV file",
    )
    args = parser.parse_args()

    main(args.file, args.dumpdata)
