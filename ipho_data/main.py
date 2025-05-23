#!/usr/bin/env python
# Author:  Mario S. Könz <mskoenz@gmx.net>


# pylint: disable=unused-import, import-error, useless-suppression
import sys

import non_install_helper

import ipho_data.django_setup
from ipho_data.test_data_creator import TestDataCreator


def set_up_basic_test_database():

    tdc = TestDataCreator(data_path="test_data", master_seed=0)

    tdc.init_database()
    tdc.create_groups()
    tdc.create_olyexams_superuser(pw_strategy="create")
    tdc.create_organizer_user(pw_strategy="trivial")
    tdc.create_delegation_user(pw_strategy="trivial")
    tdc.create_examsite_user(pw_strategy="trivial")
    tdc.create_students()

    voting_room = "room"
    if voting_room is not None:
        voting_room_2 = voting_room + "2"
        voting_room_1 = voting_room + "1"
        voting_room = voting_room_2
        tdc.create_voting_room(voting_room_1)
        # create a second voting room, to enable switching between rooms.
        tdc.create_voting_room(voting_room_2)
        # Create votings for the second room
        tdc.create_three_poll_votings(room_name=voting_room_1)
    tdc.create_three_poll_votings(room_name=voting_room)
    tdc.create_official_delegation()
    tdc.create_ipho2016_theory_exam()
    experiment = tdc.create_ipho2016_experiment_exam()
    tdc.put_students_in_teams(experiment)


def argv_flush_confirmed():
    if "--flush" in sys.argv:
        confirm = input(
            "Are you sure you want to irreversibly flush the database? Type 'flush' to confirm: "
        )
        if confirm.lower() == "flush":
            return True

        print("ABORTED FLUSHING: setting up database without flushing...")
    return False


def main(flush=False):
    # flush the database
    if flush or argv_flush_confirmed():
        print("Flushing the database...")
        from django.core.management import call_command

        call_command("flush", interactive=False)

    set_up_basic_test_database()


if __name__ == "__main__":
    main()
