import shutil
from pathlib import Path
from contextlib import contextmanager, suppress

from django.conf import settings
from django.db import connections
from django.utils import lorem_ipsum

from ipho_core.models import Delegation
from ipho_exam.models import Question
from ipho_marking.models import MarkingAction


from ipho_data.ipho2016_qml_data import IPHO2016_DATA
from ipho_data.data_creator import DataCreator

DEFAULT_DATABASE_NAME = settings.DATABASES["default"]["NAME"]


class TestDataCreator(DataCreator):
    def __init__(self, db_name=None, data_path="test_data", **kwgs):
        data_path = Path(__file__).parent / data_path
        super().__init__(data_path, **kwgs)

        db_setting = settings.DATABASES["default"]
        if "sqlite3" in db_setting["ENGINE"]:
            if db_name is None:
                db_name = DEFAULT_DATABASE_NAME
            self.db_filepath = Path(settings.PROJECT_PATH) / db_name
            self.db_filepath.parent.mkdir(parents=True, exist_ok=True)
            db_setting["NAME"] = str(self.db_filepath)
            connections["default"].settings_dict["NAME"] = db_setting["NAME"]

    def copy_from(self, copy_from):
        shutil.copy(copy_from.db_filepath, self.db_filepath)

    def delete_database(self):
        if not "sqlite3" in settings.DATABASES["default"]["ENGINE"]:
            raise RuntimeError("delete_database is only allowed for sqlite3 backend")
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
        self.create_poll_que("Q1", "How is it going", None, y="good", m="meh", n="bad")

        self.create_poll_que("Q2", "Current day", None, d="weekday", e="weekend")

        que3 = self.create_poll_que(
            "Q3", "Favorite color", None, r="red", b="blue", g="green"
        )
        self.close_poll_que_with_result(que3, r=1, b=2, g=3)

    def create_feedback_for_question(self, question, comment=None):
        for deleg in Delegation.objects.all():
            if comment is None:
                tmp_comment = f"{deleg.country} " + lorem_ipsum.paragraphs(1, True)[0]
            else:
                tmp_comment = comment
            self.create_feedback(
                question=question,
                delegation=deleg,
                comment=tmp_comment,
                part="A.1",
                qml_id="q0_ti1",
            )

    def create_ipho2016_theory_exam(self):
        exam = self.create_exam(name="Theory", code="T")
        gen_inst = self.create_question(
            exam, name="General Instructions", code="G", position=0, type=self.QUESTION
        )
        phases = self.create_exam_phases_for_exam(exam)
        self.set_exam_to_phase(phases[4])
        self.create_official_version_node(gen_inst, text=IPHO2016_DATA["T-G0-v1"])
        self.create_official_version_node(
            gen_inst, text=IPHO2016_DATA["T-G0-final"], version=2
        )
        lang1 = self.create_language_from_code(code="AUS", name="TestLanguage1")
        self.create_translation_node(
            gen_inst, lang1, text=IPHO2016_DATA["T-G0-transl1"]
        )
        lang2 = self.create_language_from_code(code="AUS", name="TestLanguage2")
        self.create_translation_node(
            gen_inst, lang2, text=IPHO2016_DATA["T-G0-transl2"]
        )
        lang3 = self.create_language_from_code(code="AUT", name="TestLanguage3")
        self.create_translation_node(
            gen_inst, lang3, text=IPHO2016_DATA["T-G0-transl3"]
        )

        que1 = self.create_question(
            exam,
            name="Two Problems in Mechanics",
            code="Q",
            position=1,
            type=self.QUESTION,
        )
        self.create_official_version_node(que1, text=IPHO2016_DATA["T-Q1-final"])
        self.create_translation_node(que1, lang1, text=IPHO2016_DATA["T-Q1-final"])
        self.create_feedback_for_question(que1)

        ans1 = self.create_question(
            exam,
            name="Two Problems in Mechanics - Answer Sheet",
            code="A",
            position=1,
            type=self.ANSWER,
            working_pages=6,
        )
        self.create_official_version_node(ans1, text=IPHO2016_DATA["T-A1-final"])
        self.create_translation_node(ans1, lang1, text=IPHO2016_DATA["T-A1-final"])

        que2 = self.create_question(
            exam,
            name="Two Problems in Mechanics",
            code="Q",
            position=2,
            type=self.QUESTION,
        )
        self.create_official_version_node(que2, text=IPHO2016_DATA["T-Q2-final"])
        self.create_translation_node(que2, lang1, text=IPHO2016_DATA["T-Q2-final"])

        ans2 = self.create_question(
            exam,
            name="Nonlinear Dynamics in Electric Circuits - Answer Sheet",
            code="A",
            position=2,
            type=self.ANSWER,
            working_pages=6,
        )
        self.create_official_version_node(ans2, text=IPHO2016_DATA["T-A2-final"])
        self.create_translation_node(ans2, lang1, text=IPHO2016_DATA["T-A2-final"])

        self.create_figures_with_ids(
            fig_ids=IPHO2016_DATA["FIGURE_IDS"], filename="logo_square.png"
        )

        return exam

    def create_ipho2016_marking(self, all_actions_open=False):
        answer1 = Question.objects.get(name="Two Problems in Mechanics - Answer Sheet")
        answer2 = Question.objects.get(
            name="Nonlinear Dynamics in Electric Circuits - Answer Sheet"
        )

        self.set_zero_points(delegation_code="CHE", question=answer1, version="O")
        self.set_max_points(delegation_code="CHE", question=answer1, version="D")
        self.set_zero_points(delegation_code="ARM", question=answer1, version="O")
        self.set_max_points(delegation_code="ARM", question=answer1, version="D")
        self.set_zero_points(delegation_code="AUS", question=answer1, version="O")
        self.set_max_points(delegation_code="AUS", question=answer1, version="D")
        self.set_max_points(delegation_code="AUS", question=answer1, version="F")

        self.set_zero_points(delegation_code="AUT", question=answer1, version="O")
        self.set_max_points(delegation_code="AUT", question=answer1, version="D")
        self.set_max_points(delegation_code="AUT", question=answer1, version="F")
        self.set_zero_points(delegation_code="AUT", question=answer2, version="O")
        self.set_max_points(delegation_code="AUT", question=answer2, version="D")
        self.set_max_points(delegation_code="AUT", question=answer2, version="F")

        if all_actions_open:
            pass  # MarkingActions are open per default
        else:
            self.set_marking_status(
                delegation_code="CHE", question=answer1, status=MarkingAction.OPEN
            )
            self.set_marking_status(
                delegation_code="ARM",
                question=answer1,
                status=MarkingAction.SUBMITTED_FOR_MODERATION,
            )
            self.set_marking_status(
                delegation_code="AUS",
                question=answer1,
                status=MarkingAction.LOCKED_BY_MODERATION,
            )
            self.set_marking_status(
                delegation_code="AUT", question=answer1, status=MarkingAction.FINAL
            )
            self.set_marking_status(
                delegation_code="AUT", question=answer2, status=MarkingAction.FINAL
            )
