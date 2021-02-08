from collections import defaultdict

from ipho_core.models import Participant, Delegation
from ipho_exam.models import Exam, Place

from .base_data import BaseDataCreator


class ParticipantDataCreator(BaseDataCreator):
    def _create_participant(
        self, *, first_name, last_name, delegation_code, participant_code
    ):
        deleg = Delegation.objects.get(name=delegation_code)
        ppnt, created = Participant.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            delegation=deleg,
            code=participant_code,
        )
        if created:
            ppnt.save()
            self.log(ppnt, "..", "created")
        return ppnt

    def create_participants(self, file="022_participants.csv", fieldnames=None):
        if fieldnames is None:
            fieldnames = ["first_name", "last_name", "delegation", "code"]

        generate_code = "code" not in fieldnames
        deleg_participant_count = defaultdict(int)
        for participant_data in self.read_csv(file, fieldnames):
            if generate_code:
                deleg_participant_count[participant_data.delegation] += 1
                participant_data.code = f"{participant_data.delegation}-S-{deleg_participant_count[participant_data.delegation]}"

            self._create_participant(
                first_name=participant_data.first_name,
                last_name=participant_data.last_name,
                delegation_code=participant_data.delegation,
                participant_code=participant_data.code,
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
