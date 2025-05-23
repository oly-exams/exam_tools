#!/usr/bin/env python
# Author:  Mario S. Könz <mskoenz@gmx.net>


# pylint: disable=unused-import, import-error, useless-suppression
import non_install_helper

import ipho_data.django_setup
from ipho_data.test_data_creator import TestDataCreator


def set_up_basic_training_database():

    tdc = TestDataCreator(data_path="training_data", master_seed=0)

    tdc.init_database()
    tdc.create_groups()
    tdc.create_olyexams_superuser(pw_strategy="create")
    tdc.create_organizer_user(pw_strategy="trivial")
    tdc.create_delegation_user(pw_strategy="trivial")
    tdc.create_examsite_user(pw_strategy="trivial")
    tdc.create_students()

    tdc.create_three_poll_votings()
    tdc.create_official_delegation()
    tdc.create_ipho2016_theory_exam()
    tdc.create_ipho2016_experiment_exam()
    # tdc.put_students_in_teams(experiment)


def main():
    set_up_basic_training_database()


if __name__ == "__main__":
    main()
