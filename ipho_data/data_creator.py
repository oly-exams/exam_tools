from .creator.user_data import UserDataCreator
from .creator.poll_data import PollDataCreator
from .creator.official_delegation import OfficialDelegDataCreator
from .creator.exam_and_question import ExamAndQuestionDataCreator


class DataCreator(
    UserDataCreator,
    PollDataCreator,
    OfficialDelegDataCreator,
    ExamAndQuestionDataCreator,
):
    pass
