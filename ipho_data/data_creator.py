from .creator.user_data import UserDataCreator
from .creator.question_data import QuestionDataCreator
from .creator.official_delegation import OfficialDelegDataCreator
from .creator.exam_and_question import ExamAndQuestionDataCreator


class DataCreator(
    UserDataCreator,
    QuestionDataCreator,
    OfficialDelegDataCreator,
    ExamAndQuestionDataCreator,
):
    pass
