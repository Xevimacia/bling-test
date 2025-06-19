import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, CardFactory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def card(user):
    return CardFactory(user=user) 