from .creator.control import ExamPhaseDataCreator
from .creator.exam_and_question import ExamAndQuestionDataCreator
from .creator.feedback import FeedbackDataCreator
from .creator.figure import FigureDataCreator
from .creator.language import LanguageDataCreator
from .creator.marking_data import MarkingDataCreator
from .creator.official_delegation import OfficialDelegDataCreator
from .creator.poll_data import PollDataCreator
from .creator.students_and_seatings import StudentDataCreator
from .creator.user_data import UserDataCreator


class DataCreator(
    UserDataCreator,
    PollDataCreator,
    OfficialDelegDataCreator,
    ExamAndQuestionDataCreator,
    FigureDataCreator,
    ExamPhaseDataCreator,
    LanguageDataCreator,
    FeedbackDataCreator,
    StudentDataCreator,
    MarkingDataCreator,
):
    pass
