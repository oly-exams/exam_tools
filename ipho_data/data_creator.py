from .creator.user_data import UserDataCreator
from .creator.poll_data import PollDataCreator
from .creator.official_delegation import OfficialDelegDataCreator
from .creator.exam_and_question import ExamAndQuestionDataCreator
from .creator.language import LanguageDataCreator
from .creator.feedback import FeedbackDataCreator
from .creator.control import ExamPhaseDataCreator
from .creator.students_and_seatings import StudentDataCreator
from .creator.marking_data import MarkingDataCreator


class DataCreator(
    UserDataCreator,
    PollDataCreator,
    OfficialDelegDataCreator,
    ExamAndQuestionDataCreator,
    ExamPhaseDataCreator,
    LanguageDataCreator,
    FeedbackDataCreator,
    StudentDataCreator,
    MarkingDataCreator,
):
    pass
