import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import django

django.setup()

import csv

from ipho_core.models import Delegation, Student


def main(input):
    reader = csv.DictReader(input)

    for i, row in enumerate(reader):
        # print(row)
        try:
            ## Delegation
            delegation = Delegation.objects.get(name=row["delegation"])

            participant, created = Student.objects.get_or_create(
                code=row["code"],
                defaults={
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "delegation": delegation,
                },
            )
            if created:
                print(participant, "..", "created")

        except Delegation.DoesNotExist:
            print("Skip", row["code"], "because delegation does not exist.")
        except KeyError:
            pass
            # print(row['code'])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import CSV with users")
    parser.add_argument(
        "file",
        type=argparse.FileType("rU", encoding="utf-8-sig"),
        help="Input CSV file",
    )
    args = parser.parse_args()

    main(args.file)
