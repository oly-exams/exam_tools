from .creator.user_data import UserDataCreator
from .creator.question_data import QuestionDataCreator
from .creator.official_delegation import OfficialDelegDataCreator


class DataCreator(UserDataCreator, QuestionDataCreator, OfficialDelegDataCreator):
    pass
