# pylint: disable=redefined-builtin

from ipho_exam.models import Exam, Question, Language, VersionNode

from .base_data import BaseDataCreator


class ExamAndQuestionDataCreator(BaseDataCreator):
    QUESTION = Question.QUESTION
    ANSWER = Question.ANSWER

    def create_exam(self, *, code, name):
        exam = Exam.objects.create(code=code, name=name)
        exam.save()
        self.log(exam, "..", "created")

        return exam

    def create_question(self, exam, *, name, code, position, type, **kwgs):
        valid_types = [self.QUESTION, self.ANSWER]
        if type not in valid_types:
            raise NotImplementedError(
                f"the type '{type}' you selected is not supported, use on of {valid_types}"
            )
        que = Question.objects.create(
            exam=exam, code=code, name=name, position=position, type=type, **kwgs
        )
        que.save()
        self.log(que, "..", "created")

        return que

    def create_official_version_node(self, que, *, text, version=1):
        ofcl_lang = Language.get_official()
        vsnode = VersionNode.objects.create(
            question=que, language=ofcl_lang, text=text, version=version
        )
        vsnode.save()
        self.log(vsnode, "..", "created")
        return vsnode
