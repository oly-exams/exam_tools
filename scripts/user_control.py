# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
sys.path.append(".")

import django

django.setup()

from ipho_core.models import User


def enable_disable(users, enable):
    for user in users:
        db_user = User.objects.get(username=user)
        db_user.is_active = enable
        db_user.save()

        print(user, "enabled" if enable else "disabled")


def enable_disable_all(enable, group):
    for db_user in User.objects.filter(groups__name=group):
        db_user.is_active = enable
        db_user.save()

        print(db_user, "enabled" if enable else "disabled")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enable or disable users")
    parser.add_argument(
        "-e",
        "--enable",
        nargs="+",
        help="Enable the given users (example --enable CHN VNM)",
    )
    parser.add_argument(
        "-d",
        "--disable",
        nargs="+",
        help="Disable the given users (example --disable CHE)",
    )
    parser.add_argument(
        "--enable-all-delegations",
        help="Enable all delegation users",
        action="store_true",
    )
    parser.add_argument(
        "--disable-all-delegations",
        help="Disable all delegation users",
        action="store_true",
    )
    parser.add_argument(
        "--enable-all-examsites",
        help="Enable all examsite users",
        action="store_true",
    )
    parser.add_argument(
        "--disable-all-examsites",
        help="Disable all examsite users",
        action="store_true",
    )
    args = parser.parse_args()

    if args.enable:
        enable_disable(args.enable, enable=True)
    if args.disable:
        enable_disable(args.disable, enable=False)
    if args.enable_all_delegations:
        enable_disable_all(enable=True, group="Delegation")
    if args.disable_all_delegations:
        enable_disable_all(enable=False, group="Delegation")
    if args.enable_all_examsites:
        enable_disable_all(enable=True, group="Delegation Examsite Team")
    if args.disable_all_examsites:
        enable_disable_all(enable=False, group="Delegation Examsite Team")
