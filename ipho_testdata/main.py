#!/usr/bin/env python
# Author:  Mario S. Könz <mskoenz@gmx.net>


import non_install_helper
import django_setup

from test_data_creator import TestDataCreator


def main():
    tdc = TestDataCreator(master_seed=0)
    with tdc.clean(delete_after=False):
        tdc.create_permissions()
        tdc.create_groups()
        tdc.create_olyexams_superuser(pw_strategy="trivial")
        tdc.create_organizer_user(pw_strategy="trivial")
        tdc.create_delegation_user(pw_strategy="trivial")


if __name__ == "__main__":
    main()
