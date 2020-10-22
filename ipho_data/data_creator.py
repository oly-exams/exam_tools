from .creator.user_data import UserDataCreator
from .creator.question_data import QuestionDataCreator


class DataCreator(UserDataCreator, QuestionDataCreator):
    pass
