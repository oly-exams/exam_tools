#!/usr/bin/env python
# Author:  Mario S. Könz <mskoenz@gmx.net>

# pylint: disable=unused-import
import non_install_helper  # pylint: disable=import-error

import ipho_data.django_setup
from ipho_data.test_data_creator import TestDataCreator


def set_up_basic_test_database(clear_cache=False):

    # the cache speeds up the process, since the base data is the same
    cache = TestDataCreator("precache.db", data_path="test_data_cypress", master_seed=0)
    if clear_cache:
        cache.delete_database()
    if not cache.db_filepath.exists():
        cache.init_database()
        cache.create_permissions()
        cache.create_groups()
        # cache.create_olyexams_superuser(pw_strategy="create")
        cache.create_organizer_user(pw_strategy="trivial")
        cache.create_delegation_user(pw_strategy="trivial")

    tdc = TestDataCreator(data_path="test_data_cypress")

    with tdc.clean(delete_after=False):
        tdc.copy_from(cache)
        tdc.create_three_questions()


def main():
    set_up_basic_test_database(clear_cache=True)


if __name__ == "__main__":
    main()
