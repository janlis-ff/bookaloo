import pytest
from rest_framework.test import APIClient

from bookaloo.users.models import User
from bookaloo.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def anonymous_client() -> APIClient:
    return APIClient()
