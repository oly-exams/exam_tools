import sys
import csv
import string
from pathlib import Path
from collections import namedtuple
from contextlib import contextmanager, suppress

import iso3166

from django.core.management import call_command
from django.conf import settings

from django.contrib.auth.models import Permission
from ipho_core.models import Group, User
from ipho_core.models import Delegation, AutoLogin
from ipho_poll.models import VotingRight

from ipho_testdata.password_creator import PasswordCreator


class DataCreatorUtilities:
    @staticmethod
    def log(*args):
        sys.stderr.write(" ".join([str(a) for a in args]) + "\n")

    def read_csv(self, csv_filename, fieldnames):
        RowTuple = namedtuple("RowTuple", fieldnames)  # pylint: disable=invalid-name
        with self.full_path(csv_filename).open("r") as f:
            reader = csv.reader(f)
            iterat = map(RowTuple._make, reader)
            header = next(iter)
            self.check_header_vs_fieldnames(header, fieldnames, csv_filename)
            yield from iterat

    def full_path(self, filename):  # pylint: disable=no-self-use
        raise NotImplementedError()

    @staticmethod
    def check_header_vs_fieldnames(header, fieldnames, filename):
        for head, name in zip(header, fieldnames):
            if head.replace(" ", "").lower() != name.replace("_", "").lower():
                raise ValueError(
                    f"Your file header is '{head}' while your fieldname is '{name}' in file {filename}. They are only allowed to differ by capitalization and whitespace to underscore mapping."
                )


class DataCreator(DataCreatorUtilities):
    def __init__(self, data_path, master_seed=None):
        self.data_path = data_path
        self.pw_creator = PasswordCreator(self, master_seed)

    def full_path(self, filename):
        return self.data_path / filename

    @staticmethod
    def flush_database():
        call_command("flush", interactive=False)

    @staticmethod
    def init_database():
        call_command("migrate", verbose=0)

    def load_data(self, json_filename):
        call_command("loaddata", self.full_path(json_filename))

    def create_permissions(self):
        self.load_data("000_django_permissions.json")

    def create_groups(self):
        self.load_data("001_groups.json")

    def create_olyexams_superuser(self, pw_strategy="create"):
        fieldnames = ["username", "first_name", "last_name"]
        self._create_users(
            "010_olyexams_superuser.csv",
            fieldnames,
            pw_strategy,
            is_superuser=True,
            group="Admin",
        )

    def create_organizer_user(self, pw_strategy="create"):
        fieldnames = ["username", "first_name", "last_name", "group", "voting_power"]
        self._create_users("011_organizer_user.csv", fieldnames, pw_strategy)

    def _create_users(self, filename_csv, fieldnames, pw_strategy, **kwgs):
        with self.pw_creator.create_pw_gen(filename_csv, pw_strategy) as pw_gen:
            for user_data in self.read_csv(filename_csv, fieldnames):
                password = pw_gen(user_data.username)
                self._create_user(
                    self._create_normal_voting,
                    password=password,
                    **user_data._asdict(),
                    **kwgs,
                )

    def _create_user(
        self,
        create_voting,
        *,
        password,
        is_superuser=False,
        group="",
        voting_power=0,
        **user_data,
    ):
        is_staff = group == "Admin"
        user, created = User.objects.get_or_create(
            **user_data, is_superuser=is_superuser, is_staff=is_staff
        )
        if group:
            user.groups.add(Group.objects.get(name=group))

        user.set_password(password)
        assert user.check_password(password)

        if voting_power:
            voting_power = int(voting_power)
            if voting_power > 0:
                user.user_permissions.add(Permission.objects.get(name="Can vote"))

            for i in range(voting_power):
                create_voting(user, i)

        user.save()
        if created:
            self.log(user, "..", "created")
        return user

    def _create_normal_voting(self, user, i):  # pylint: disable=unused-argument
        voting_right, created = VotingRight.objects.get_or_create(
            user=user, name=f"{user.first_name} {user.last_name}"
        )
        if created:
            self.log(voting_right, "..", "created")

    def _create_delegation_voting(self, user, i):
        letter = string.ascii_uppercase[i]
        voting_right, created = VotingRight.objects.get_or_create(
            user=user, name=f"Leader {letter}"
        )
        if created:
            self.log(voting_right, "..", "created")

    def create_delegation_user(self, pw_strategy="create", enforce_iso3166=True):
        filename_csv = "020_delegations.csv"
        fieldnames = ["country_name", "country_code", "voting_power"]
        with self.pw_creator.create_pw_gen(filename_csv, pw_strategy) as pw_gen:
            for deleg_data in self.read_csv(filename_csv, fieldnames):
                if enforce_iso3166:
                    self._enforce_iso3166(deleg_data)

                country_name, country_code, voting_power = deleg_data
                username = country_code
                password = pw_gen(username)

                delegation = self._create_delegation(country_name, country_code)
                user = self._create_user(
                    self._create_delegation_voting,
                    username=username,
                    password=password,
                    voting_power=voting_power,
                )

                if not hasattr(user, "autologin"):
                    autologin = AutoLogin(user=user)
                    autologin.save()
                    self.log("Autologin created")

                delegation.members.add(user)
                delegation.save()

    def _create_delegation(self, country_name, country_code):
        delegation, created = Delegation.objects.get_or_create(
            name=country_code, country=country_name
        )
        if created:
            self.log(delegation, "..", "created")

        return delegation

    @staticmethod
    def _enforce_iso3166(deleg_data):
        if deleg_data.country_code not in iso3166.countries_by_alpha3:
            raise ValueError(
                f"{deleg_data.country_code} is not a valid iso3166 3-letter shortcut, valid options are {list(iso3166.countries_by_alpha3)}"
            )
        if not any(
            x.startswith(deleg_data.country_name.upper())
            for x in iso3166.countries_by_name
        ):
            suggestions = list(
                x
                for x in filter(
                    lambda x: x.startswith(deleg_data.country_name[0]),
                    iso3166.countries_by_name,
                )
            )
            raise ValueError(
                f"{deleg_data.country_name} is not a valid iso3166 country name, did you mean one of {suggestions}"
            )


class TestDataCreator(DataCreator):
    def __init__(self, db_name=None, **kwgs):
        data_path = Path(__file__).parent / "test_data"

        db_setting = settings.DATABASES["default"]
        if "sqlite3" not in db_setting["ENGINE"]:
            raise RuntimeError("TestDataCreator supports only sqlite3 at the moment")

        super().__init__(data_path, **kwgs)

        if db_name is not None:
            db_setting["NAME"] = db_name
        else:
            db_name = db_setting["NAME"]
        self.db_filepath = Path(settings.PROJECT_PATH) / db_name

    def delete_database(self):
        with suppress(FileNotFoundError):
            self.db_filepath.unlink()

    @contextmanager
    def clean(self, delete_after=True):
        self.delete_database()
        self.init_database()
        try:
            yield
        finally:
            # always delete the database if not manually specified not to
            if delete_after:
                self.delete_database()
