from django.conf import settings

from ipho_core.models import Delegation
from ipho_exam.models import Language

from .base_data import BaseDataCreator


class OfficialDelegDataCreator(BaseDataCreator):
    def create_official_delegation(self):
        official = settings.OFFICIAL_DELEGATION
        deleg = Delegation.objects.create(name=official, country=official)
        deleg.save()
        self.log(deleg, "..", "created")

        lang = Language.objects.create(name="English", delegation=deleg, versioned=True)
        self.log(lang, "..", "created")

        if lang.id != 1:
            raise RuntimeError(
                f"The official language needs to have id='1' (for now), but instead has id='{lang.id}'"
            )

        assert lang.is_official()
        lang.save()

        return deleg
