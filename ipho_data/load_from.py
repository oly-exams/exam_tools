#!/usr/bin/env python
# Author:  Mario S. Könz <mskoenz@gmx.net>

import os
import sys
from pathlib import Path

# pylint: disable=unused-import, import-error, useless-suppression
import non_install_helper

# this file should only be run on the remote, where we have a settings file

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import ipho_data.django_setup
from ipho_data.test_data_creator import TestDataCreator


def load_from_data_path(data_path):

    tdc = TestDataCreator(data_path=data_path)

    tdc.init_database()
    tdc.create_groups()
    tdc.create_olyexams_superuser(pw_strategy="read")
    tdc.create_organizer_user(pw_strategy="read")
    tdc.create_delegation_user(pw_strategy="read", enforce_iso3166=True)
    tdc.create_official_delegation()

    for name in ["Theory", "Experiment"]:
        exam = tdc.create_exam(name=name, code=name[0])
        tdc.create_exam_phases_for_exam(exam)

    return tdc


def main():
    if len(sys.argv) < 2:
        print("please use load_from.py path [ipho2016]")
        return
    path = Path(sys.argv[1])
    tdc = load_from_data_path(path)
    if len(sys.argv) > 2:
        for argv in sys.argv[2:]:
            if argv == "ipho2016":
                tdc.create_ipho2016_theory_exam_only()
            elif argv == "remote":
                tdc.create_examsite_user(pw_strategy="read", enforce_iso3166=True)
            elif argv == "students":
                tdc.create_students()
            elif argv == "test_votings":
                tdc.create_three_poll_votings()


if __name__ == "__main__":
    main()
