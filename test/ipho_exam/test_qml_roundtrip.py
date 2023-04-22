import pytest

from ipho_exam.models import Language


@pytest.mark.django_db
def test_foo():
    lang = Language.objects.create(name="FooBar")
    lang.save()
    assert Language.objects.all().count() == 1
