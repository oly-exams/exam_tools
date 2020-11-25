from ipho_marking.models import (
    generate_markings_from_exam,
    Marking,
    MarkingMeta,
    MarkingAction,
)
from ipho_core.models import Delegation

from .base_data import BaseDataCreator


OFFICIAL_LANGUAGE_PK = 1


class MarkingDataCreator(BaseDataCreator):
    def import_markings_from_exam(self, exam):
        (
            num_tot,
            num_created,
            num_marking_tot,
            num_marking_created,
        ) = generate_markings_from_exam(exam)
        self.log(f"{num_marking_tot} Markings", "..", "imported")
        return {
            "total": num_tot,
            "created": num_created,
            "marking_total": num_marking_tot,
            "marking_created": num_marking_created,
        }

    def _change_marking(
        self, *, student, meta, version, points
    ):  # pylint: disable=no-self-use
        marking = Marking.objects.get(
            student=student, marking_meta=meta, version=version
        )
        marking.points = points
        marking.save()

    def _set_max_points_marking(
        self, *, student, meta, version
    ):  # pylint: disable=no-self-use
        marking = Marking.objects.get(
            student=student, marking_meta=meta, version=version
        )
        marking.points = meta.max_points
        marking.save()

    def _set_max_points_question(self, *, student, question, version):
        metas = MarkingMeta.objects.filter(question=question)
        for meta in metas:
            self._set_max_points_marking(student=student, meta=meta, version=version)

    def set_max_points(self, *, delegation_code, question, version):
        deleg = Delegation.objects.get(name=delegation_code)
        for stud in deleg.student_set.all():
            self._set_max_points_question(
                student=stud, question=question, version=version
            )

    def _set_zero_points_question(self, *, student, question, version):
        metas = MarkingMeta.objects.filter(question=question)
        for meta in metas:
            self._change_marking(student=student, meta=meta, version=version, points=0)

    def set_zero_points(self, *, delegation_code, question, version):
        deleg = Delegation.objects.get(name=delegation_code)
        for stud in deleg.student_set.all():
            self._set_zero_points_question(
                student=stud, question=question, version=version
            )

    @staticmethod
    def set_marking_status(*, delegation_code, question, status):
        deleg = Delegation.objects.get(name=delegation_code)
        action = MarkingAction.objects.get(
            delegation=deleg,
            question=question,
        )
        action.status = status
        action.save()
