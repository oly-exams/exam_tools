from ipho_control.models import ExamPhase

from .base_data import BaseDataCreator


class ExamPhaseDataCreator(BaseDataCreator):
    def _create_exam_phase(self, *, exam, name, position, exam_settings, **kwargs):
        default_kwargs = {
            "description": f"Description Phase {name} of {exam}",
            "public_description": f"Public description Phase {name} of {exam}",
            "before_switching": f"Before switching Phase {name} of {exam}",
            "available_to_organizers": True,
            "available_question_settings": [],
            "checks_warning": [],
            "checks_error": [],
            "exam": exam,
            "name": name,
            "position": position,
            "exam_settings": exam_settings,
        }
        default_kwargs.update(kwargs)
        phase, created = ExamPhase.objects.get_or_create(**default_kwargs)
        # Validate phase (validates e.g. exam setting choices)
        if created:
            phase.full_clean()
            phase.save()
            self.log(phase, "..", "created")
        return phase

    def create_exam_phases_for_exam(self, exam, filename_json="041_exam_phases.json"):
        phases_kwargs = self.read_json(filename_json)
        phases = []
        for kwargs in phases_kwargs:
            phase = self._create_exam_phase(exam=exam, **kwargs)
            phases.append(phase)
        return phases

    def set_exam_to_phase(self, phase):
        phase.apply()
