import pytest
from cards.services import CardService
from cards.models import Card
from users.models import CustomUser
from django.db import IntegrityError
from django.utils import timezone

@pytest.mark.django_db
class TestCardService:
    def test_create_card_valid_black(self, mocker, user):
        """Creates a black card with valid data and checks all fields."""
        mock_provider = mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card")
        mock_provider.return_value = {
            "expiration_date": "2024-01-01T12:00:00+00:00",
            "id": "prov_id",
            "color": "COLOR_2",
            "status": "ORDERED"
        }
        card = CardService.create_card(user, "black")
        assert card.color == "black"
        assert card.external_id == "prov_id"
        assert card.status == "ORDERED"
        assert timezone.is_aware(card.expiration_date)

    def test_create_card_valid_pink(self, mocker, user):
        """Creates a pink card with valid data and checks all fields."""
        mock_provider = mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card")
        mock_provider.return_value = {
            "expiration_date": "2024-01-01T12:00:00+00:00",
            "id": "prov_id2",
            "color": "COLOR_1",
            "status": "ORDERED"
        }
        card = CardService.create_card(user, "pink")
        assert card.color == "pink"
        assert card.external_id == "prov_id2"
        assert card.status == "ORDERED"
        assert timezone.is_aware(card.expiration_date)

    def test_create_card_invalid_color(self, user):
        """Raises ValueError for invalid color."""
        with pytest.raises(ValueError):
            CardService.create_card(user, "blue")

    def test_create_card_invalid_external_id(self, user):
        """Raises ValueError for invalid external_id."""
        with pytest.raises(ValueError):
            CardService.create_card(user, "black", external_id="something_else")

    def test_create_card_provider_error_provider_error(self, mocker, user):
        """Raises RuntimeError if provider_error external_id is used."""
        mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card", side_effect=Exception("Provider error"))
        with pytest.raises(RuntimeError):
            CardService.create_card(user, "black", external_id="provider_error")

    def test_create_card_provider_error_invalid_user_id(self, mocker, user):
        """Raises RuntimeError if invalid_user_id external_id is used."""
        mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card", side_effect=Exception("User not found"))
        with pytest.raises(RuntimeError):
            CardService.create_card(user, "black", external_id="invalid_user_id") 

    def test_create_card_db_error(self, mocker, user):
        """Raises RuntimeError if DB save fails."""
        mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card", return_value={
            "expiration_date": "2024-01-01T12:00:00+00:00",
            "id": "prov_id",
            "color": "COLOR_2",
            "status": "ORDERED"
        })
        mocker.patch("cards.models.Card.objects.create", side_effect=IntegrityError("DB error"))
        with pytest.raises(RuntimeError):
            CardService.create_card(user, "black")

    def test_create_card_expiration_date_timezone_aware(self, mocker, user):
        """Ensures expiration_date is made timezone-aware if provider returns naive datetime."""
        naive_date = "2024-01-01T12:00:00"
        mock_provider = mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card")
        mock_provider.return_value = {
            "expiration_date": naive_date,
            "id": "prov_id",
            "color": "COLOR_2",
            "status": "ORDERED"
        }
        card = CardService.create_card(user, "black")
        assert timezone.is_aware(card.expiration_date)

    def test_list_user_cards(self, user, card):
        """Returns all cards for the user."""
        cards = list(CardService.list_user_cards(user))
        assert card in cards

    def test_retrieve_user_card(self, user, card):
        """Retrieves a specific card by pk for the user."""
        found = CardService.retrieve_user_card(user, card.pk)
        assert found == card

    def test_retrieve_user_card_not_found(self, user):
        """Raises DoesNotExist if card does not exist for user."""
        with pytest.raises(Card.DoesNotExist):
            CardService.retrieve_user_card(user, 99999)

    def test_create_card_provider_missing_status(self, mocker, user):
        """Raises RuntimeError if provider omits status."""
        mock_provider = mocker.patch("providers.clients.bank_provider.BankProviderClient.create_card")
        mock_provider.return_value = {
            "expiration_date": "2024-01-01T12:00:00+00:00",
            "id": "prov_id",
            "color": "COLOR_2"
            # status omitted
        }
        with pytest.raises(RuntimeError, match="Provider did not return status"):
            CardService.create_card(user, "black")