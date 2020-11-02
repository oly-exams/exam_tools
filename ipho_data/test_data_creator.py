import shutil
from pathlib import Path
from contextlib import contextmanager, suppress

from django.conf import settings
from django.db import connections

from ipho_data.ipho2016_qml_data import IPHO2016_DATA
from ipho_data.data_creator import DataCreator

DEFAULT_DATABASE_NAME = settings.DATABASES["default"]["NAME"]


class TestDataCreator(DataCreator):
    def __init__(self, db_name=None, data_path="test_data", **kwgs):
        data_path = Path(__file__).parent / data_path

        db_setting = settings.DATABASES["default"]
        if "sqlite3" not in db_setting["ENGINE"]:
            raise RuntimeError("TestDataCreator supports only sqlite3 at the moment")

        super().__init__(data_path, **kwgs)

        if db_name is None:
            db_name = DEFAULT_DATABASE_NAME
        self.db_filepath = Path(settings.PROJECT_PATH) / db_name

        db_setting["NAME"] = str(self.db_filepath)
        connections["default"].settings_dict["NAME"] = db_setting["NAME"]

    def copy_from(self, copy_from):
        shutil.copy(copy_from.db_filepath, self.db_filepath)

    def delete_database(self):
        with suppress(FileNotFoundError):
            self.db_filepath.unlink()

    @contextmanager
    def clean(self, delete_after=True):
        # this is necessary when changing db names (caching)
        connections["default"].close()
        self.delete_database()
        try:
            yield
        finally:
            # always delete the database if not manually specified not to
            if delete_after:
                self.delete_database()

    def create_three_poll_questions(self):
        self.create_poll_que("Q1", "How is it going", y="good", m="meh", n="bad")

        self.create_poll_que("Q2", "Current day", d="weekday", e="weekend")

        que3 = self.create_poll_que(
            "Q3", "Favorite color", r="red", b="blue", g="green"
        )
        self.close_poll_que_with_result(que3, r=1, b=2, g=3)

    def create_ipho2016_theory_exam(self):
        exam = self.create_exam(name="Theory", code="T")
        gen_inst = self.create_question(
            exam, name="General Instructions", code="G", position=0, type=self.QUESTION
        )
        self.create_official_version_node(gen_inst, text=IPHO2016_DATA["T-G0-final"])
        que1 = self.create_question(
            exam,
            name="Two Problems in Mechanics",
            code="Q",
            position=1,
            type=self.QUESTION,
        )
        self.create_official_version_node(que1, text=IPHO2016_DATA["T-Q1-final"])
        ans1 = self.create_question(
            exam,
            name="Two Problems in Mechanics - Answer Sheet",
            code="A",
            position=1,
            type=self.ANSWER,
            working_pages=6,
        )
        self.create_official_version_node(ans1, text=IPHO2016_DATA["T-A1-final"])
        que2 = self.create_question(
            exam,
            name="Two Problems in Mechanics",
            code="Q",
            position=2,
            type=self.QUESTION,
        )
        self.create_official_version_node(que2, text=IPHO2016_DATA["T-Q2-final"])
        ans2 = self.create_question(
            exam,
            name="Nonlinear Dynamics in Electric Circuits - Answer Sheet",
            code="A",
            position=2,
            type=self.ANSWER,
            working_pages=6,
        )
        self.create_official_version_node(ans2, text=IPHO2016_DATA["T-A2-final"])
