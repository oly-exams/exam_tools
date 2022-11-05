import sys
import csv
import json
from collections import namedtuple

from django.core.management import call_command


class CreatorCsvUtil:
    @staticmethod
    def log(*args):
        sys.stderr.write(" ".join([str(a) for a in args]) + "\n")

    def read_csv(self, csv_filename, fieldnames):
        RowTuple = namedtuple("RowTuple", fieldnames)  # pylint: disable=invalid-name
        with self.full_path(csv_filename).open("r") as f:
            reader = csv.reader(f)
            iterat = map(RowTuple._make, reader)
            try:
                header = next(iterat)
                self.check_header_vs_fieldnames(header, fieldnames, csv_filename)
                yield from iterat
            except StopIteration:
                return

    def full_path(self, filename):
        raise NotImplementedError()

    @staticmethod
    def check_header_vs_fieldnames(header, fieldnames, filename):
        for head, name in zip(header, fieldnames):
            if head.replace(" ", "").lower() != name.replace("_", "").lower():
                raise ValueError(
                    f"Your file header is '{head}' while your fieldname is '{name}' in file {filename}. They are only allowed to differ by capitalization and whitespace to underscore mapping."
                )


class CreatorJsonUtil:
    def full_path(self, filename):
        raise NotImplementedError()

    def read_json(self, json_filename):
        with self.full_path(json_filename).open("r") as f:
            return json.load(f)


class BaseDataCreator(CreatorCsvUtil, CreatorJsonUtil):
    def __init__(self, data_path):
        self.data_path = data_path

    def full_path(self, filename):
        return self.data_path / filename

    @staticmethod
    def flush_database():
        call_command("flush", interactive=False)

    @staticmethod
    def init_database():
        call_command("migrate", verbosity=0)

    def load_data(self, json_filename):
        call_command("loaddata", self.full_path(json_filename))

    def create_permissions(self):
        self.load_data("000_django_permissions.json")

    def create_groups(self):
        self.load_data("001_groups.json")
