#!/usr/bin/env python
# Author:  Mario S. Könz <mskoenz@gmx.net>

import sys

# pylint: disable=unused-import, import-error
import non_install_helper

import ipho_data.django_setup
from ipho_data.test_data_creator import TestDataCreator


def set_up_basic_test_database(clear_cache=False):

    # the cache speeds up the process, since the base data is the same
    cache = TestDataCreator("precache.db", master_seed=0)
    if clear_cache:
        cache.delete_database()
    if not cache.db_filepath.exists():
        cache.init_database()
        cache.create_groups()
        cache.create_olyexams_superuser(pw_strategy="create")
        cache.create_organizer_user(pw_strategy="trivial")
        cache.create_delegation_user(pw_strategy="trivial")
        cache.create_three_poll_questions()

    tdc = TestDataCreator()

    with tdc.clean(delete_after=False):
        tdc.copy_from(cache)
        tdc.create_official_delegation()
        tdc.create_ipho2016_theory_exam()


def main():
    clear = False
    if len(sys.argv) > 1:
        clear = bool(sys.argv[1])
    set_up_basic_test_database(clear_cache=clear)


if __name__ == "__main__":
    main()
