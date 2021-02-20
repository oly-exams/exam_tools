from collections import defaultdict

from ipho_core.models import Student, Delegation
from ipho_exam.models import Participant, Exam, Place

from .base_data import BaseDataCreator


class StudentDataCreator(BaseDataCreator):
    def _create_student(self, *, first_name, last_name, delegation_code, student_code):
        deleg = Delegation.objects.get(name=delegation_code)
        ppnt, created = Student.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            delegation=deleg,
            code=student_code,
        )
        if created:
            ppnt.save()
            self.log(ppnt, "..", "created")
        return ppnt

    def create_students(self, file="022_students.csv", fieldnames=None):
        if fieldnames is None:
            fieldnames = ["first_name", "last_name", "delegation", "code"]

        generate_code = "code" not in fieldnames
        deleg_student_count = defaultdict(int)
        for student_data in self.read_csv(file, fieldnames):
            if generate_code:
                deleg_student_count[student_data.delegation] += 1
                student_data.code = f"{student_data.delegation}-S-{deleg_student_count[student_data.delegation]}"

            self._create_student(
                first_name=student_data.first_name,
                last_name=student_data.last_name,
                delegation_code=student_data.delegation,
                student_code=student_data.code,
            )

    def _create_seating(self, *, participant_id, exam_name, place_name):
        ppnt = Participant.objects.get(code=participant_id)
        exam = Exam.objects.get(name=exam_name)
        place, cre = Place.objects.update_or_create(
            participant=ppnt,
            exam=exam,
            name=place_name,
        )
        if cre:
            self.log(place, "..", "created")
        else:
            self.log(place, "..", "updated")
        return place

    def create_seatings(self, file="040_participant_seatings.csv", fieldnames=None):
        if fieldnames is None:
            fieldnames = ["participant", "exam", "place"]
        for seating_data in self.read_csv(file, fieldnames):
            self._create_seating(
                participant_id=seating_data.participant,
                exam_name=seating_data.exam,
                place_name=seating_data.place,
            )
