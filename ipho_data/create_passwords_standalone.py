#!/usr/bin/env python

import csv
import sys
from pathlib import Path

import non_install_helper  # pylint: disable=unused-import,import-error

from ipho_data.creator.base_data import BaseDataCreator
from ipho_data.creator.password_creator import PasswordCreator


def main():
    if len(sys.argv) < 3:
        print(f"usage: {sys.argv[0]} path_to_initial_data master_seed")
        return
    path = Path(sys.argv[1]).resolve()
    master_seed = int(sys.argv[2])

    if (path / "pws").exists():
        print("cannot create passwords, the directory exists already!")
        return

    data_creator = BaseDataCreator(path)
    pw_creator = PasswordCreator(data_creator, master_seed)

    for filename_csv, username in [
        ("010_olyexams_superuser.csv", "{Username}"),
        ("011_organizer_user.csv", "{Username}"),
        ("020_delegations.csv", "{Country Code}"),
        ("021_examsite_user.csv", "{Country Code}-Examsite"),
    ]:
        with pw_creator.create_pw_gen(filename_csv, "create") as pw_gen:
            with open(path / filename_csv, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for x in reader:
                    pw_gen(username.format_map(x))


if __name__ == "__main__":
    main()
