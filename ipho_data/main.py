#!/usr/bin/env python
# Author:  Mario S. Könz <mskoenz@gmx.net>


# pylint: disable=unused-import, import-error, useless-suppression
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


def main():
    set_up_basic_test_database()


if __name__ == "__main__":
    main()
