#!/usr/bin/env python
# Author:  Mario S. Könz <mskoenz@gmx.net>

# pylint: disable=unused-import, import-error, useless-suppression
import non_install_helper

import ipho_data.django_setup
from ipho_data.test_data_creator import TestDataCreator


def set_up_basic_test_database():
    tdc = TestDataCreator(data_path="test_data_cypress")

    tdc.init_database()
    tdc.create_groups()
    # tdc.create_olyexams_superuser(pw_strategy="create")
    tdc.create_organizer_user(pw_strategy="trivial")
    tdc.create_delegation_user(pw_strategy="trivial")
    tdc.create_students()
    tdc.create_three_poll_questions()
    tdc.create_official_delegation()
    exam = tdc.create_ipho2016_theory_exam()
    tdc.create_language_from_code(code="ARM", name="TestLanguage")
    tdc.create_seatings()
    tdc.import_markings_from_exam(exam)
    tdc.create_ipho2016_marking()


def main():
    set_up_basic_test_database()


if __name__ == "__main__":
    main()
