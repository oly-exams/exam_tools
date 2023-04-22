#!/usr/bin/env python
# Author:  Mario S. Könz <mskoenz@gmx.net>

import os
import sys
from pathlib import Path

# pylint: disable=unused-import, import-error, useless-suppression
import non_install_helper

# this file should only be run on the remote, where we have a settings file

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exam_tools.settings")

import ipho_data.django_setup
from ipho_data.test_data_creator import TestDataCreator


def load_from_data_path(data_path, enforce_iso3166):

    tdc = TestDataCreator(data_path=data_path)

    tdc.init_database()
    tdc.create_groups()
    tdc.create_olyexams_superuser(pw_strategy="read")
    tdc.create_organizer_user(pw_strategy="read")
    tdc.create_delegation_user(pw_strategy="read", enforce_iso3166=enforce_iso3166)
    tdc.create_official_delegation()

    return tdc


def main():  # pylint: disable=too-many-branches
    if len(sys.argv) < 2:
        print(
            "please use load_from.py path [skip-iso] [ipho2016] [students] [remote] [mock]"
        )
        return
    path = Path(sys.argv[1]).resolve()

    enforce_iso3166 = True
    if len(sys.argv) > 2 and sys.argv[2] == "skip-iso":
        print("\033[1;31mskipping iso3166 checking\033[0m")
        enforce_iso3166 = False

    tdc = load_from_data_path(path, enforce_iso3166)
    if len(sys.argv) > 2:
        for argv in sys.argv[2:]:
            if argv == "ipho2016":
                tdc.create_ipho2016_theory_exam_only()
            elif argv == "ibo2019":
                tdc.create_ibo2019_theory_exam()
                tdc.create_ibo2019_experimental_exam()
            elif argv == "remote":
                tdc.create_examsite_user(
                    pw_strategy="read", enforce_iso3166=enforce_iso3166
                )
            elif argv == "skip-iso":
                pass
            elif argv == "students":
                tdc.create_students()
            elif argv == "test_votings":
                tdc.create_three_poll_votings()
            elif argv == "mock":
                tdc.create_mock_theory_exam()
            elif argv == "figures_from_folder":
                tdc.create_figures_from_folder(folder="figures")
            else:  # assuming it an exam name to be created
                name = argv
                code = name[0]
                if ":" in argv:
                    code, name = argv.split(":", 1)
                exam = tdc.create_exam(name=name, code=code)
                tdc.create_exam_phases_for_exam(exam)


if __name__ == "__main__":
    main()
