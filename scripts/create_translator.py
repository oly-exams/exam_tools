# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import django

django.setup()

import csv
from ipho_core.models import Delegation, Student, User, Group, AutoLogin
from ipho_exam.models import Language, TranslationNode, Exam


def main(input):
    reader = csv.DictReader(input)

    delegations_group = Group.objects.get(name="Delegation")
    for i, row in enumerate(reader):
        name = "Tr-" + row["First name"][0] + row["Last name"][0]
        delegation, _ = Delegation.objects.get_or_create(
            name=name,
            defaults={"country": "{} {}".format(row["First name"], row["Last name"])},
        )

        user, created = User.objects.get_or_create(
            username=row["Username"],
            defaults={
                "last_name": row["Last name"],
                "first_name": row["First name"],
                "email": row["Email"],
            },
        )
        if created:
            user.set_password(row["Password"])
            user.save()

        user.groups.add(delegations_group)
        user.save()

        delegation.members.add(user)
        delegation.save()

        language, _ = Language.objects.get_or_create(
            name=row["Language"], delegation=delegation
        )
        for exam in Exam.objects.all():
            for q in exam.question_set.all():
                node, _ = TranslationNode.objects.get_or_create(
                    question=q,
                    language=language,
                    defaults={"text": '<question id="q0" />'},
                )
        print(row["Username"], "...", "imported.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import CSV with translators")
    parser.add_argument("file", type=argparse.FileType("rU"), help="Input CSV file")
    args = parser.parse_args()

    main(args.file)
