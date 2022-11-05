# pylint: disable=redefined-builtin

from ipho_exam.models import Exam, Question, Language, VersionNode, TranslationNode

from .base_data import BaseDataCreator


class ExamAndQuestionDataCreator(BaseDataCreator):
    QUESTION = Question.QUESTION
    ANSWER = Question.ANSWER

    def create_exam(self, *, code, name):
        exam, created = Exam.objects.get_or_create(code=code, name=name)
        if created:
            exam.save()
            self.log(exam, "..", "created")

        return exam

    def create_question(self, exam, *, name, code, position, type, **kwgs):
        valid_types = [self.QUESTION, self.ANSWER]
        if type not in valid_types:
            raise NotImplementedError(
                f"the type '{type}' you selected is not supported, use on of {valid_types}"
            )
        que, created = Question.objects.get_or_create(
            exam=exam, code=code, name=name, position=position, type=type, **kwgs
        )
        if created:
            que.save()
            self.log(que, "..", "created")

        return que

    def create_official_version_node(self, que, *, text, version=1, status="C"):
        ofcl_lang = Language.get_official()
        vsnode, created = VersionNode.objects.get_or_create(
            question=que,
            language=ofcl_lang,
            text=text,
            version=version,
            status=status,
        )
        if created:
            vsnode.save()
            self.log(vsnode, "..", "created")
        return vsnode

    def create_translation_node(self, que, lang, *, text, status="O"):
        tnode, created = TranslationNode.objects.get_or_create(
            question=que,
            language=lang,
            text=text,
            status=status,
        )
        if created:
            tnode.save()
            self.log(tnode, "..", "created")
        return tnode
