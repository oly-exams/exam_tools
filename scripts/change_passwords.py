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

import os
import secrets
import string
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import django

django.setup()

import csv

from ipho_core.models import Delegation


def log(*args):
    sys.stderr.write(" ".join([str(a) for a in args]) + "\n")


alphabet = "23456789ABCDEFGHJKLMNPRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
password_length = 8


def get_password():
    return "".join(secrets.choice(alphabet) for i in range(password_length))


def main(change_delegations=False, change_examsite=False):

    delegations = Delegation.objects.all()

    with open("new_passwords.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Country Name", "Username", "Password"])
        for deleg in delegations:
            for user in deleg.members.all():
                if (
                    change_delegations
                    and user.groups.filter(name="Delegation").exists()
                ) or (
                    change_examsite
                    and user.groups.filter(name="Delegation Examsite Team").exists()
                ):
                    pw = get_password()
                    user.set_password(pw)
                    user.save()
                    writer.writerow([deleg.country, user.username, pw])
                    log(deleg.country, user.username, ".. changed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Change passwords")
    parser.add_argument(
        "--examsite", action="store_true", help="Change passwords of examsite users"
    )
    parser.add_argument(
        "--delegations",
        action="store_true",
        help="Change passwords of delegation users",
    )

    args = parser.parse_args()

    main(args.delegations, args.examsite)
