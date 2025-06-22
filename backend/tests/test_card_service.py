import pytest
import requests
from cards.services import CardService
from cards.models import Card
from users.models import CustomUser
from django.db import IntegrityError
from django.utils import timezone
from cards.exceptions import UserNotRegisteredError, ProviderFailureError, InvalidCardDataError, InvalidInputError, CardNotFoundError

@pytest.mark.django_db
class TestCardService:
    @pytest.mark.parametrize("color", ["black", "pink"])
    def test_create_card_valid(self, mocker, user, color):
        """Creates a card with valid data by mocking the provider."""
        # Arrange: Mock the provider client to return a predictable, successful response.
        mock_provider = mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card")
        mock_provider.return_value = {
            "expiration_date": (timezone.now() + timezone.timedelta(days=365)).isoformat(),
            "id": "prov_id_123",
            "status": "ORDERED",
        }

        # Act
        card = CardService.create_card(user, color)

        # Assert
        assert card.color == color
        assert card.external_id == "prov_id_123"
        assert card.status == "ORDERED"
        assert timezone.is_aware(card.expiration_date)
        assert card.expiration_date > timezone.now()

    def test_create_card_provider_error(self, mocker, user):
        """Raises ProviderFailureError if the provider call fails with a 500-level error."""
        # Simulate a 500 error from the provider
        mock_response = mocker.Mock()
        mock_response.status_code = 500
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card", side_effect=http_error)

        with pytest.raises(ProviderFailureError):
            CardService.create_card(user, "black")

    def test_create_card_invalid_user_id(self, mocker, user):
        """Raises UserNotRegisteredError if the provider call fails with a 400-level error."""
        # Simulate a 400 error from the provider
        mock_response = mocker.Mock()
        mock_response.status_code = 400
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card", side_effect=http_error)

        with pytest.raises(UserNotRegisteredError):
            CardService.create_card(user, "black")

    def test_create_card_db_error(self, mocker, user):
        """Raises RuntimeError if DB save fails."""
        # Mock the part that fails: the database save.
        mocker.patch("cards.models.Card.objects.create", side_effect=IntegrityError("DB error"))
        with pytest.raises(RuntimeError):
            CardService.create_card(user, "black")

    def test_create_card_expiration_date_timezone_aware(self, mocker, user):
        """Ensures expiration_date is made timezone-aware if provider returns naive datetime."""
        # Use a fixed future naive date string to test timezone conversion.
        naive_date_str = "2099-01-01T12:00:00"
        mock_provider = mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card")
        mock_provider.return_value = {
            "expiration_date": naive_date_str,
            "id": "prov_id",
            "color": "COLOR_2",
            "status": "ORDERED"
        }
        card = CardService.create_card(user, "black")
        assert timezone.is_aware(card.expiration_date)

    def test_create_card_with_past_expiration_date(self, mocker, user):
        """Raises InvalidCardDataError if expiration date is in the past."""
        past_date = timezone.now() - timezone.timedelta(days=1)
        mock_provider = mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card")
        mock_provider.return_value = {
            "expiration_date": past_date.isoformat(),
            "id": "prov_id",
            "color": "COLOR_2",
            "status": "ORDERED"
        }
        with pytest.raises(InvalidCardDataError):
            CardService.create_card(user, "black")

    def test_create_card_without_expiration_date(self, mocker, user):
        """Tests that a card can be created without an expiration date."""
        mock_provider = mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card")
        mock_provider.return_value = {
            # No expiration_date
            "id": "prov_id",
            "color": "COLOR_2",
            "status": "ORDERED"
        }
        card = CardService.create_card(user, "black")
        assert card is not None
        assert card.expiration_date is None

    def test_create_card_provider_missing_status(self, mocker, user):
        """Raises ProviderFailureError if provider omits status."""
        mock_provider = mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card")
        mock_provider.return_value = {
            # Date is still needed to pass the date validation step.
            "expiration_date": "2099-01-01T12:00:00+00:00",
            "id": "prov_id",
            "color": "COLOR_2"
            # status omitted
        }
        with pytest.raises(ProviderFailureError):
            CardService.create_card(user, "black")

    def test_list_user_cards(self, user, card):
        """Returns all cards for the user."""
        cards = list(CardService.list_user_cards(user))
        assert card in cards

    def test_retrieve_user_card(self, user, card):
        """Retrieves a specific card by pk for the user."""
        found = CardService.retrieve_user_card(user, card.pk)
        assert found == card

    def test_retrieve_user_card_not_found(self, user):
        """Raises CardNotFoundError if card does not exist for user."""
        with pytest.raises(CardNotFoundError):
            CardService.retrieve_user_card(user, 99999)