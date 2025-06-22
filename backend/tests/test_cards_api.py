import pytest
import requests
from cards.models import Card
from tests.factories import UserFactory
from django.utils import timezone
from cards.exceptions import ProviderFailureError

@pytest.mark.django_db
class TestCardAPI:
    endpoint = "/api/cards/"

    @pytest.mark.parametrize("color", ["black", "pink"])
    def test_create_card_success(self, auth_client, user, color):
        """Tests that an authenticated user can successfully create a card with valid data. Verifies the response status, returned data, and that the card exists in the database."""
        data = {"color": color}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 201
        assert response.data["color"] == color
        assert Card.objects.filter(user=user, color=color).exists()
        assert response.data["expiration_date"] is not None
        assert response.data["status"] == "ORDERED"

    def test_create_card_invalid_color(self, auth_client):
        """Tests that creating a card with an invalid color ('blue') returns a 400 Bad Request response, indicating validation failure."""
        data = {"color": "blue"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 400

    def test_create_card_missing_color(self, auth_client):
        """Tests that creating a card without specifying a color returns a 400 Bad Request response, ensuring required fields are validated."""
        data = {}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 400

    def test_create_card_provider_error(self, mocker, auth_client):
        """Tests that a provider error returns a 502 Bad Gateway response."""
        mock_response = mocker.Mock()
        mock_response.status_code = 500
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card", side_effect=http_error)

        data = {"color": "black"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 502
        assert response.data["error"] == "provider_unavailable"
        assert "trace_id" in response.data

    def test_create_card_invalid_user_id(self, mocker, auth_client):
        """Tests that a 400 from the provider returns a 400 Bad Request."""
        mock_response = mocker.Mock()
        mock_response.status_code = 400
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card", side_effect=http_error)
        
        data = {"color": "black"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 400
        assert response.data["error"] == "user_not_registered"
        assert "trace_id" in response.data

    def test_create_card_db_error(self, mocker, auth_client):
        """Tests that if a database error occurs, the API responds with a 500 Internal Server Error."""
        mocker.patch("cards.services.Card.objects.create", side_effect=Exception("DB error"))
        data = {"color": "black"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 500
        assert "unexpected error" in response.data["detail"].lower()
        assert "trace_id" in response.data

    def test_create_card_unauthenticated(self, api_client):
        """Tests that an unauthenticated user cannot create a card and receives a 401 Unauthorized response."""
        data = {"color": "black"}
        response = api_client.post(self.endpoint, data)
        assert response.status_code == 401

    def test_create_card_unexpected_exception(self, mocker, auth_client):
        """If service raises unexpected exception, API returns 500."""
        mocker.patch("cards.services.CardService.create_card", side_effect=Exception("Unexpected"))
        data = {"color": "black"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 500
        assert "unexpected error" in response.data["detail"].lower()
        assert "trace_id" in response.data

    def test_create_card_provider_missing_status(self, mocker, auth_client):
        """Tests that if the provider omits 'status', the API returns a 502 error."""
        mock_provider = mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card")
        mock_provider.return_value = {
            "expiration_date": "2099-01-01T12:00:00+00:00",
            "id": "prov_id",
            "color": "COLOR_2"
            # status omitted
        }
        data = {"color": "black"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 502
        assert response.data["error"] == "missing_status"
        assert "trace_id" in response.data

    def test_retrieve_own_card_success(self, auth_client, card):
        """Tests that an authenticated user can retrieve their own card by ID, and the response contains the correct card data."""
        url = f"{self.endpoint}{card.id}/"
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.data["id"] == card.id

    def test_retrieve_card_not_found(self, auth_client):
        """Tests that requesting a non-existent card ID returns a 404 Not Found response."""
        url = f"{self.endpoint}9999/"
        response = auth_client.get(url)
        assert response.status_code == 404

    def test_retrieve_card_not_owned(self, auth_client, card):
        """Tests that a user cannot retrieve a card owned by another user; the API should return a 404 Not Found response for unauthorized access."""
        other_user = UserFactory()
        card.user = other_user
        card.save()
        url = f"{self.endpoint}{card.id}/"
        response = auth_client.get(url)
        assert response.status_code == 404

    def test_retrieve_unauthenticated(self, api_client, card):
        """Tests that an unauthenticated user cannot retrieve a card and receives a 401 Unauthorized response."""
        url = f"{self.endpoint}{card.id}/"
        response = api_client.get(url)
        assert response.status_code == 401

    def test_list_cards_success(self, auth_client, card):
        """Tests that an authenticated user can list their cards, and the response includes the expected card."""
        response = auth_client.get(self.endpoint)
        assert response.status_code == 200
        assert any(c["id"] == card.id for c in response.data)

    def test_list_cards_empty(self, auth_client):
        """Tests that when an authenticated user has no cards, the API returns an empty list with a 200 OK status."""
        response = auth_client.get(self.endpoint)
        assert response.status_code == 200
        assert response.data == []

    def test_list_unauthenticated(self, api_client):
        """Tests that an unauthenticated user cannot list cards and receives a 401 Unauthorized response."""
        response = api_client.get(self.endpoint)
        assert response.status_code == 401