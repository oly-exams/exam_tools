import csv
import random
import datetime
import collections
from contextlib import contextmanager


class PasswordCreator:
    def __init__(self, data_creator, master_seed):
        self.data_creator = data_creator

        if master_seed is None:
            master_seed = datetime.date.today().year

        seed_rng = random.Random(master_seed)

        self._seed_for = {}

        self._seed_for["010_olyexams_superuser.csv"] = seed_rng.randint(0, 100000)
        self._seed_for["011_organizer_user.csv"] = seed_rng.randint(0, 100000)
        self._seed_for["020_delegations.csv"] = seed_rng.randint(0, 100000)
        self._seed_for["021_supervisor_user.csv"] = seed_rng.randint(0, 100000)

    @staticmethod
    def generate_password(length, rng):
        valid_chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789"
        return "".join(rng.sample(valid_chars, length))

    def _read_pw_mapping(self, assoz_filename):
        filepath = self._get_filepath_pw_mapping(assoz_filename)
        return self._read_pw_mapping_filepath(filepath)

    @staticmethod
    def _read_pw_mapping_filepath(filepath):
        pw_mapping = collections.OrderedDict()
        with filepath.open("r") as f:
            reader = csv.reader(f)
            next(reader)
            for user, password in reader:
                pw_mapping[user] = password

        return pw_mapping

    def _write_pw_mapping(self, assoz_filename, pw_mapping):
        filepath = self._get_filepath_pw_mapping(assoz_filename)
        with filepath.open("w") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password"])
            for data in pw_mapping.items():
                writer.writerow(data)

    def _get_filepath_pw_mapping(self, assoz_filename):
        # 010_olyexams_superusers.csv -> pw/olyexams_superusers_credentials.csv
        filename = (
            f"pws/{assoz_filename.split('_', 1)[1].rsplit('.', 1)[0]}_credentials.csv"
        )
        filepath = self.data_creator.full_path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        return filepath

    def _prevent_identical_pw_check(self, assoz_filename, pw_mapping):
        new_pws = list(pw_mapping.values())
        new_pws = list(filter(lambda x: x != "1234", new_pws))

        if len(set(new_pws)) != len(new_pws):
            raise ValueError(
                f"There are non trivial (1234) pws repeated in '{new_pws}'"
            )
        new_pws = set(new_pws)

        filepath = self._get_filepath_pw_mapping(assoz_filename)
        for file in filepath.parent.iterdir():
            if file == filepath:
                continue

            other_pw_mapping = self._read_pw_mapping_filepath(file)
            other_pws = list(other_pw_mapping.values())
            other_pws = set(filter(lambda x: x != "1234", other_pws))

            intersect = new_pws.intersection(other_pws)
            if intersect:
                raise ValueError(
                    f"your {len(new_pws)} new passwords for '{filepath.stem}' intersect {len(intersect)} times with file '{file.stem}'. Do not use the same seed!"
                )

    @contextmanager
    def create_pw_gen(self, filename_csv, pw_strategy):
        pw_mapping = collections.OrderedDict()
        if pw_strategy == "create":
            rng = random.Random()
            sub_seed = self._seed_for[filename_csv]
            self.data_creator.log("creating passwords with sub-seed", sub_seed)
            rng.seed(sub_seed)

        if pw_strategy == "read":
            pw_mapping = self._read_pw_mapping(filename_csv)

        def pw_generator(username):
            if pw_strategy == "create":
                password = self.generate_password(8, rng)
                pw_mapping[username] = password
            elif pw_strategy == "trivial":
                password = "1234"
                pw_mapping[username] = password
            elif pw_strategy == "read":
                password = pw_mapping[username]
            else:
                raise NotImplementedError(pw_strategy)
            return password

        yield pw_generator

        if pw_strategy != "read":
            self._prevent_identical_pw_check(filename_csv, pw_mapping)
            self._write_pw_mapping(filename_csv, pw_mapping)
