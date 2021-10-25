#!/usr/bin/env python
# Author:  Mario S. Könz <mskoenz@gmx.net>

import sys
from pathlib import Path

# pylint: disable=unused-import, import-error, useless-suppression
import non_install_helper

import ipho_data.django_setup
from ipho_data.test_data_creator import TestDataCreator


def load_from_data_path(data_path, pw_strat, seed):

    tdc = TestDataCreator(data_path=data_path, master_seed=seed)

    tdc.init_database()
    tdc.create_groups()
    tdc.create_olyexams_superuser(pw_strategy=pw_strat)
    tdc.create_organizer_user(pw_strategy=pw_strat)
    tdc.create_delegation_user(pw_strategy=pw_strat, enforce_iso3166=True)
    tdc.create_official_delegation()

    for i in "ABCDE":
        exam = tdc.create_exam(name=f"Exam-{i}", code=i)
        tdc.create_exam_phases_for_exam(exam)
    # exam = tdc.create_exam(name="Experiment", code="E")
    # tdc.create_exam_phases_for_exam(exam)
    return tdc


def main():
    if len(sys.argv) < 4:
        print(
            "please use load_from.py path pw_strat (create/read) master_seed [ipho2016]"
        )
        return
    path = Path(sys.argv[1])
    pw_strat = sys.argv[2]
    seed = int(sys.argv[3])
    tdc = load_from_data_path(path, pw_strat, seed)
    if len(sys.argv) == 5:
        if sys.argv[4] == "ipho2016":
            tdc.create_ipho2016_theory_exam("IPhO2016-Theory")


if __name__ == "__main__":
    main()
