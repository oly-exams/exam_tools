import string
import iso3166

from django.contrib.auth.models import Permission

from ipho_core.models import Group, User
from ipho_core.models import Delegation, AutoLogin
from ipho_poll.models import VotingRight

from .base_data import BaseDataCreator
from .password_creator import PasswordCreator


class UserDataCreator(BaseDataCreator):
    def __init__(self, *args, master_seed=None, **kwgs):
        super().__init__(*args, **kwgs)
        self._pw_creator = PasswordCreator(self, master_seed)

    def create_olyexams_superuser(self, pw_strategy="create"):
        if pw_strategy == "trivial":
            raise NotImplementedError(
                "We do not allow trivial passwords for superusers"
            )

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

    def create_delegation_user(self, pw_strategy="create", enforce_iso3166=True):
        filename_csv = "020_delegations.csv"
        fieldnames = ["country_name", "country_code", "voting_power"]
        with self._pw_creator.create_pw_gen(filename_csv, pw_strategy) as pw_gen:
            for deleg_data in self.read_csv(filename_csv, fieldnames):
                if enforce_iso3166:
                    self._enforce_iso3166(
                        deleg_data.country_code, deleg_data.country_name
                    )

                country_name, country_code, voting_power = deleg_data
                username = country_code + "-Leader"
                password = pw_gen(username)

                delegation = self._create_delegation(country_name, country_code)
                user = self._create_user(
                    self._create_delegation_voting,
                    username=username,
                    password=password,
                    voting_power=voting_power,
                    group="Delegation",
                )

                if not hasattr(user, "autologin"):
                    autologin = AutoLogin(user=user)
                    autologin.save()
                    self.log("Autologin created")

                delegation.members.add(user)
                delegation.save()

    def create_examsite_user(self, pw_strategy="create", enforce_iso3166=True):
        filename_csv = "021_supervisor_user.csv"
        fieldnames = ["country_code"]
        with self._pw_creator.create_pw_gen(filename_csv, pw_strategy) as pw_gen:
            for deleg_data in self.read_csv(filename_csv, fieldnames):
                if enforce_iso3166:
                    self._enforce_iso3166(deleg_data.country_code)

                country_code = deleg_data.country_code
                username = country_code + "-Supervisor"
                password = pw_gen(username)
                user = self._create_user(
                    self._create_delegation_voting,
                    username=username,
                    password=password,
                    group="Delegation Examsite Team",
                )
                if not hasattr(user, "autologin"):
                    autologin = AutoLogin(user=user)
                    autologin.save()
                    self.log("Autologin created")

                delegation = Delegation.objects.get(name=country_code)
                delegation.members.add(user)
                delegation.save()

    def _create_users(self, filename_csv, fieldnames, pw_strategy, **kwgs):
        with self._pw_creator.create_pw_gen(filename_csv, pw_strategy) as pw_gen:
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
        if not created:
            return user
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

    def _create_delegation(self, country_name, country_code):
        delegation, created = Delegation.objects.get_or_create(
            name=country_code, country=country_name
        )
        if created:
            self.log(delegation, "..", "created")

        return delegation

    @staticmethod
    def _enforce_iso3166(country_code, country_name=None):
        if country_code not in iso3166.countries_by_alpha3:
            raise ValueError(
                f"{country_code} is not a valid iso3166 3-letter shortcut, valid options are {list(iso3166.countries_by_alpha3)}"
            )
        if country_name is None:
            return

        # allow United States and United Kingdom, since official names are longer
        if not any(
            x.startswith(country_name.upper())
            for x in iso3166.countries_by_name  # is all caps
        ):
            # suggest only countries that start with the same letter
            suggestions = list(
                x
                for x in filter(
                    lambda x: x.startswith(country_name[0]),
                    iso3166.countries_by_name,
                )
            )
            raise ValueError(
                f"{country_name} is not a valid iso3166 country name, did you mean one of {suggestions}"
            )
