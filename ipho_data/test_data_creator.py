from pathlib import Path
from contextlib import contextmanager, suppress

from django.conf import settings


from ipho_data.data_creator import DataCreator


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
