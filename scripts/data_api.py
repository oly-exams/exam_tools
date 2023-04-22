import subprocess
import os
import sys

sys.path.append(".")

import datetime
import argparse
import contextlib
import collections
import csv
import itertools

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"


@contextlib.contextmanager
def redirect_stdout(fn):
    old_stdout = sys.stdout
    with open(fn, "w") as f:
        sys.stdout = f
        yield
        sys.stdout = old_stdout


with redirect_stdout(os.devnull):
    import django

    django.setup()

import django.contrib.auth.models
import ipho_core.models
import ipho_exam.models
import ipho_marking.models
import django.core


demo_input_folder = "data/demo_input"
demo_output_folder = "data/demo"

base_manage_args = ["python", "manage.py"]
base_manage_loaddata_args = base_manage_args + ["loaddata"]
base_manage_dumpdata_args = base_manage_args + [
    "dumpdata",
    "--natural-foreign",
    "--natural-primary",
    "--indent=2",
]


ObjectStore = collections.namedtuple("ObjectStore", ["object", "existed"])


def execute_subprocess(args, stdout=None):
    if stdout is None:
        stdout = subprocess.DEVNULL
    elif isinstance(stdout, str):
        stdout = open(stdout, "w")
    subprocess.run(
        args, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdout=stdout
    ).check_returncode()


def flush_database():
    execute_subprocess(base_manage_args + ["flush", "--noinput"])


class Data:
    def __init__(self, source_folder, store_folder):
        self.source_folder = source_folder
        self.store_folder = store_folder
        self.new_objects = []

    def generate(self, prefix=""):
        pass

    def load(self, prefix="", select=False, select_only=False):
        pass

    def dump(self, prefix="", select=False, select_only=False):
        pass


class SingleTableData(Data):
    def __init__(self, index, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index
        self.model = model

    @staticmethod
    def get_table_module(model):
        return model.__module__.split(".")[-2]

    @staticmethod
    def get_table_name(model):
        return model.__name__.lower()

    @property
    def table_module(self):
        return self.get_table_module(self.model)

    @property
    def table_name(self):
        return self.get_table_name(self.model)

    @property
    def tables(self):
        return [f"{self.table_module}.{self.table_name}"]

    def get_store_file_path(self, prefix=""):
        return os.path.join(
            self.store_folder,
            f"{prefix}{self.index:03d}_{self.table_name}.json",
        )

    def get_source_file_path(self, prefix=""):
        return os.path.join(
            self.source_folder,
            f"{prefix}{self.index:03d}_{self.table_name}.csv",
        )

    def generate(self, prefix=""):
        reader = csv.DictReader(self.get_source_file_path(prefix))
        for row in reader:
            pass

    def dump(self, prefix="", select=False, select_only=False):
        if select:
            if select_only:
                items = [x.object for x in self.new_objects if not x.existed]
            else:
                items = [x.object for x in self.new_objects]
            with open(self.get_store_file_path(prefix), "w") as stream:
                django.core.serializers.serialize(
                    "json",
                    items,
                    indent=2,
                    use_natural_foreign_keys=True,
                    use_natural_primary_keys=True,
                    stream=stream,
                )
        else:
            execute_subprocess(
                base_manage_dumpdata_args + self.tables,
                self.get_store_file_path(prefix),
            )

    def load(self, prefix="", select=False, select_only=False):
        if select:
            with open(self.get_store_file_path(prefix)) as stream:
                for ser_obj in django.core.serializers.deserialize("json", stream):
                    if (
                        not select_only
                        or not type(ser_obj.object)
                        .objects.filter(
                            **{
                                field.name: getattr(ser_obj.object, field.name)
                                for field in ser_obj.object._meta.fields
                            }
                        )
                        .exists()
                    ):
                        self.new_objects.append(ObjectStore(ser_obj.object, True))
                        ser_obj.save()
        else:
            execute_subprocess(
                base_manage_loaddata_args + [self.get_store_file_path(prefix)]
            )


class ConditionSingleTableData(SingleTableData):
    def __init__(self, index, model, name, condition, *args, **kwargs):
        super().__init__(index, model, *args, **kwargs)
        self.name = name
        self.condition = condition

    @property
    def table_module(self):
        return self.get_table_module(self.model)

    @property
    def table_name(self):
        return self.name

    def dump(self, prefix="", select=False, select_only=False):
        if select and select_only:
            objs = [x.object for x in self.new_objects if not x.existed]
        elif select:
            objs = [x.object for x in self.new_objects]
        else:
            objs = self.model.objects.all()
        items = [x for x in objs if self.condition(x)]
        with open(self.get_store_file_path(prefix), "w") as stream:
            django.core.serializers.serialize(
                "json",
                items,
                indent=2,
                use_natural_foreign_keys=True,
                use_natural_primary_keys=True,
                stream=stream,
            )


class MultiTableData(SingleTableData):
    def __init__(self, index, models, name, *args, **kwargs):
        super().__init__(index, "", *args, **kwargs)
        self.models = models
        self.name = name

    @property
    def tables(self):
        return [
            f"{self.get_table_module(model)}.{self.get_table_name(model)}"
            for model in self.models
        ]

    @property
    def table_name(self):
        return self.name

    def get_store_file_path(self, prefix=""):
        return os.path.join(
            self.store_folder,
            f"{prefix}{self.index:03d}_{self.table_name}.json",
        )

    def dump(self, prefix="", select=False, select_only=False):
        if select:
            super().dump(prefix, select, select_only)
        else:
            execute_subprocess(
                base_manage_dumpdata_args + self.tables,
                self.get_store_file_path(prefix),
            )


class ConditionMultiTableData(MultiTableData):
    def __init__(self, index, models, name, conditions, *args, **kwargs):
        super().__init__(index, models, name, *args, **kwargs)
        self.conditions = conditions

    @property
    def table_module(self):
        return self.get_table_module(self.model)

    @property
    def table_name(self):
        return self.name

    def dump(self, prefix="", select=False, select_only=False):
        if select and select_only:
            objs = [x.object for x in self.new_objects if not x.existed]
        elif select:
            objs = [x.object for x in self.new_objects]
        else:
            objs = itertools.chain(*[model.objects.all() for model in self.models])
        items = [
            x
            for x in objs
            if all(
                condition(x) if isinstance(x, model) else True
                for model, condition in zip(self.models, self.conditions)
            )
        ]
        with open(self.get_store_file_path(prefix), "w") as stream:
            django.core.serializers.serialize(
                "json",
                items,
                indent=2,
                use_natural_foreign_keys=True,
                use_natural_primary_keys=True,
                stream=stream,
            )


def generate(data_elements, prefix=""):
    flush_database()
    for el in data_elements:
        el.generate(prefix)


def load(data_elements, prefix="", select=False, select_only=False):
    for el in data_elements:
        el.load(prefix, select, select_only)


def dump(data_elements, prefix="", select=False, select_only=False):
    for el in data_elements:
        el.dump(prefix, select, select_only)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate data, load and/or dump it to/from database. "
        "WARNING: this script may flush the database before loading. "
        "All previous data would be lost!"
    )

    # parser.add_argument(
    #    '-p', '--passwords', action='store_true',
    #    help='Generate missing passwords for users and delegations.')
    # parser.add_argument(
    #    '-s', '--random-seats', action='store_true',
    #    help='Generate random seats for participants.')

    parser.add_argument(
        "-i",
        "--input-folder",
        type=str,
        default=demo_input_folder,
        help="Folder containing .csv and .json data to be imported. "
        'Defaults to "{i}".'.format(i=demo_input_folder),
    )
    parser.add_argument(
        "-o",
        "--output-folder",
        type=str,
        default=demo_input_folder,
        help="Target folder for output .json files. "
        'Defaults to "{o}".'.format(o=demo_output_folder),
    )

    parser.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help="Generate data from csv/json. WARNING: database will be "
        "flushed, existing data will be lost!!",
    )
    parser.add_argument(
        "-l",
        "--load",
        action="store_true",
        help="Load data from json. Ignored if -g specified.",
    )
    parser.add_argument("-d", "--dump", action="store_true", help="Dump data to json.")

    parser.add_argument(
        "-f",
        "--flush",
        action="store_true",
        help="Flush the database before loading the new data. Ignored if "
        "-l is not set. WARNING: all existing data will be lost!!",
    )
    parser.add_argument(
        "-p", "--prefix", type=str, default="", help="Load from data with given prefix."
    )
    parser.add_argument(
        "-t",
        "--timestamp",
        action="store_true",
        help="Add timestamp (yyyymmdd_hhmmss_) to dumps.",
    )
    parser.add_argument(
        "-s",
        "--select",
        action="store_true",
        help="Dump the objects loaded/generated during this run only.",
    )
    parser.add_argument(
        "--select-only",
        action="store_true",
        help="Reinforce -s, objects loaded/generated but that already "
        "existed in the database are excluded from the dump.",
    )
    # parser.add_argument(
    #    '-m', '--models', type=str, nargs='+',
    #    help='Models to be generated/loaded/dumped.')

    args = parser.parse_args()

    if args.timestamp:
        ts_prefix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_")
    else:
        ts_prefix = ""

    data_elements = [
        SingleTableData(
            0,
            django.contrib.auth.models.Permission,
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        SingleTableData(
            1,
            django.contrib.auth.models.Group,
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        ConditionSingleTableData(
            10,
            django.contrib.auth.models.User,
            "admins",
            (lambda x: any(x.groups.filter(name="Admin"))),
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        ConditionSingleTableData(
            11,
            django.contrib.auth.models.User,
            "others",
            (lambda x: not any(x.groups.filter(name="Admin"))),
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        ConditionSingleTableData(
            20,
            ipho_core.models.Delegation,
            "delegation",
            (lambda x: x.name != "Official"),
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        SingleTableData(
            21,
            ipho_core.models.Participant,
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        SingleTableData(
            22,
            ipho_exam.models.Place,
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        SingleTableData(
            31,
            ipho_exam.models.Exam,
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        SingleTableData(
            32,
            ipho_exam.models.Question,
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        SingleTableData(
            33,
            ipho_exam.models.Figure,
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        SingleTableData(
            34,
            ipho_exam.models.VersionNode,
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        ConditionSingleTableData(
            35,
            ipho_exam.models.TranslationNode,
            "delegation_translation",
            (lambda x: x.language.delegation.name != "Official"),
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        ConditionSingleTableData(
            36,
            ipho_exam.models.Language,
            "delegation_language",
            (lambda x: x.delegation.name != "Official"),
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        ConditionSingleTableData(
            37,
            ipho_exam.models.TranslationNode,
            "official_translation",
            (lambda x: x.language.delegation.name == "Official"),
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        SingleTableData(
            50,
            ipho_exam.models.ExamAction,
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        MultiTableData(
            60,
            [ipho_marking.models.MarkingMeta, ipho_marking.models.Marking],
            "markings",
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
        ConditionMultiTableData(
            30,
            [ipho_core.models.Delegation, ipho_exam.models.Language],
            "official_delegation",
            [
                (lambda x: x.name == "Official"),
                (lambda x: x.delegation.name == "Official"),
            ],
            source_folder=args.input_folder,
            store_folder=args.output_folder,
        ),
    ]

    if args.generate:
        generate(data_elements, args.prefix)
    elif args.load:
        if args.flush:
            flush_database()
        load(data_elements, args.prefix, args.select, args.select_only)
    if args.dump:
        dump(data_elements, ts_prefix, args.select, args.select_only)
