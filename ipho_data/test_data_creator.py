import shutil
from pathlib import Path
from contextlib import contextmanager, suppress

from django.conf import settings
from django.db import connections

from ipho_data.data_creator import DataCreator

DEFAULT_DATABASE_NAME = settings.DATABASES["default"]["NAME"]


class TestDataCreator(DataCreator):
    def __init__(self, db_name=None, **kwgs):
        data_path = Path(__file__).parent / "test_data"

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

    def create_three_questions(self):
        self.create_question("Q1", "How is it going", y="good", m="meh", n="bad")

        que2 = self.create_question("Q2", "Current day", d="weekday", e="weekend")
        self.open_question_for_sec(que2, 60)

        que3 = self.create_question(
            "Q3", "Favorite color", r="red", b="blue", g="green"
        )
        self.close_question_with_result(que3, r=1, b=2, g=3)
