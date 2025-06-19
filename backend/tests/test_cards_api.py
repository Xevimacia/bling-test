import pytest
from cards.models import Card
from tests.factories import UserFactory
from django.utils import timezone

@pytest.mark.django_db
class TestCardAPI:
    endpoint = "/api/cards/"

    def test_create_card_success_black(self, auth_client, user):
        """Tests that an authenticated user can successfully create a card with valid data (color 'black'). Verifies the response status, returned data, and that the card exists in the database."""
        data = {"color": "black"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 201
        assert response.data["color"] == "black"
        assert Card.objects.filter(user=user, color="black").exists()

    def test_create_card_success_pink(self, auth_client, user):
        """Tests that an authenticated user can successfully create a card with valid data (color 'pink'). Verifies the response status, returned data, and that the card exists in the database."""
        data = {"color": "pink"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 201
        assert response.data["color"] == "pink"
        assert Card.objects.filter(user=user, color="pink").exists()

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

    def test_create_card_provider_error(self, auth_client):
        """Tests that creating a card with external_id='provider_error' simulates a provider error and returns a 502 Bad Gateway response."""
        data = {"color": "black", "external_id": "provider_error"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 502

    def test_create_card_invalid_user_id(self, auth_client):
        """Tests that creating a card with external_id='invalid_user_id' simulates a provider error and returns a 502 Bad Gateway response."""
        data = {"color": "black", "external_id": "invalid_user_id"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 502

    def test_create_card_invalid_external_id(self, auth_client):
        """Tests that creating a card with an invalid external_id (not None, not 'invalid_user_id', not 'provider_error') returns a 400 Bad Request response."""
        data = {"color": "black", "external_id": "something_else"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 400
        assert "external_id" in response.data.get("detail", "") or "Invalid external_id" in str(response.data)

    def test_create_card_db_error(self, mocker, auth_client):
        """Tests that if a database error occurs during card creation (simulated by mocking Card.objects.create to raise an exception), the API responds with a 502 Bad Gateway status."""
        mocker.patch("cards.services.Card.objects.create", side_effect=Exception("DB error"))
        data = {"color": "black"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 502

    def test_create_card_unauthenticated(self, api_client):
        """Tests that an unauthenticated user cannot create a card and receives a 401 Unauthorized response."""
        data = {"color": "black"}
        response = api_client.post(self.endpoint, data)
        assert response.status_code == 401

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

    def test_create_card_expiration_date_timezone_aware(self, mocker, auth_client):
        """Ensure expiration_date is saved as timezone-aware even if provider returns naive datetime."""
        naive_date = "2024-01-01T12:00:00"
        mock_provider = mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card")
        mock_provider.return_value = {
            "expiration_date": naive_date,
            "id": "prov_id",
            "color": "COLOR_2",
            "status": "ORDERED"
        }
        data = {"color": "black"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 201
        card = Card.objects.get(id=response.data["id"])
        assert timezone.is_aware(card.expiration_date)

    def test_create_card_unexpected_exception(self, mocker, auth_client):
        """If service raises unexpected exception, API returns 500."""
        mocker.patch("cards.services.CardService.create_card", side_effect=Exception("Unexpected"))
        data = {"color": "black"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 500
        assert "unexpected error" in response.data["detail"].lower()

    def test_create_card_provider_missing_status(self, mocker, auth_client):
        """Tests that if the provider omits 'status', the API returns a 502 error."""
        mock_provider = mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card")
        mock_provider.return_value = {
            "expiration_date": "2024-01-01T12:00:00+00:00",
            "id": "prov_id",
            "color": "COLOR_2"
            # status omitted
        }
        data = {"color": "black"}
        response = auth_client.post(self.endpoint, data)
        assert response.status_code == 502
        assert "Provider did not return status" in response.data["detail"]