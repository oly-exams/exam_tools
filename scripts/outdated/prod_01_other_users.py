import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import django

django.setup()

import csv

from django.contrib.auth.models import Permission
from django.core import serializers

from ipho_core.models import Group, User
from ipho_poll.models import VotingRight


def log(*args):
    sys.stderr.write(" ".join([str(a) for a in args]) + "\n")


def create_users(input):
    reader = csv.DictReader(input)

    created_objs = []
    can_vote = Permission.objects.get(name="Can vote")
    for i, row in enumerate(reader):
        group = None
        if row["Group"] != "":
            group = Group.objects.get(name=row["Group"])

        is_admin = row["Group"] == "Admin"
        is_super = row["Superuser"] == "yes"

        ## User
        user, created = User.objects.get_or_create(
            username=row["Username"],
            defaults={
                "first_name": row["First name"],
                "last_name": row["Last name"],
                "is_staff": is_super,
                "is_superuser": is_super,
            },
        )
        user.set_password(row["Password"])
        if group is not None:
            user.groups.add(group)
        user.save()
        if created:
            log(user, "..", "created")
        created_objs.append(user)

        ## VotingRights
        votingrights = int(int(row["VotingRight"]))
        if votingrights > 0:
            user.user_permissions.add(can_vote)
        for j in range(votingrights):
            vt, created = VotingRight.objects.get_or_create(
                user=user, name=f"{user.first_name} {user.last_name}"
            )
            if created:
                log(vt, "..", "created")
            created_objs.append(vt)
    return created_objs


def main(input, dumpdata=False):
    created_objs = create_users(input)

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

    parser = argparse.ArgumentParser(description="Import CSV to User model")
    parser.add_argument("--dumpdata", action="store_true", help="Dump Json data")
    parser.add_argument("file", type=argparse.FileType("rU"), help="Input CSV file")
    args = parser.parse_args()

    main(args.file, args.dumpdata)
