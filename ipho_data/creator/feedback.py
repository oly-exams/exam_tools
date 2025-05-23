from ipho_exam.models import Feedback

from .base_data import BaseDataCreator


class FeedbackDataCreator(BaseDataCreator):
    def create_feedback(
        self,
        *,
        question,
        delegation,
        comment,
        part,
        org_comment="",
        qml_id=None,
        status="S"
    ):
        feedback, created = Feedback.objects.get_or_create(
            delegation=delegation,
            question=question,
            comment=comment,
            org_comment=org_comment,
            part=part,
            qml_id=qml_id,
            status=status,
        )
        if created:
            feedback.save()
            self.log(feedback, "..", "created")

        return feedback
