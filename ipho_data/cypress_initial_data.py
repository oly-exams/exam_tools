#!/usr/bin/env python
# Author:  Mario S. Könz <mskoenz@gmx.net>

# pylint: disable=unused-import, import-error, useless-suppression
import argparse
import non_install_helper

import ipho_data.django_setup
from ipho_data.test_data_creator import TestDataCreator


def set_up_basic_test_database(voting_room=None):
    tdc = TestDataCreator(data_path="test_data_cypress")

    with tdc.clean(delete_after=False):
        tdc.init_database()
        tdc.create_groups()
        # tdc.create_olyexams_superuser(pw_strategy="create")
        tdc.create_organizer_user(pw_strategy="trivial")
        tdc.create_delegation_user(pw_strategy="trivial")
        tdc.create_students()
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
        theory = tdc.create_ipho2016_theory_exam()
        tdc.create_translations_and_feedback(theory)
        tdc.create_language_from_code(code="ARM", name="TestLanguage")
        tdc.create_seatings()
        tdc.import_markings_from_exam(theory)
        tdc.create_ipho2016_theory_marking()

        experiemnt = tdc.create_ipho2016_experiment_exam()
        tdc.put_students_in_teams(experiemnt)


def main(votingroom=None):
    set_up_basic_test_database(voting_room=votingroom)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a test database for cypress tests"
    )
    parser.add_argument("--votingroom")
    args = parser.parse_args()
    main(**vars(args))
