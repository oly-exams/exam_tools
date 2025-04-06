import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import django

django.setup()

import csv

from django.core import serializers

from ipho_core.models import Delegation, Group, User
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
