from ipho_exam.models import Language, Delegation

from .base_data import BaseDataCreator


class LanguageDataCreator(BaseDataCreator):
    def create_language_from_code(self, *, code, name, **kwargs):
        delegation = Delegation.objects.get(name=code)
        language = Language.objects.create(delegation=delegation, name=name, **kwargs)
        language.save()
        self.log(language, "..", "created")

        return language
