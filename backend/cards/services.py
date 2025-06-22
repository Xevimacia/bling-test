from .models import Card
from users.models import CustomUser
from providers.clients.bank_provider import BankProviderClient
from django.db import transaction
from django.utils import timezone
from dateutil.parser import isoparse
import requests
from .exceptions import UserNotRegisteredError, ProviderFailureError, InvalidCardDataError, InvalidInputError, CardNotFoundError

class CardService:
    """
    Service layer for card-related business logic. Handles creation, retrieval, and integration with external providers.
    """
    @staticmethod
    def create_card(user: CustomUser, color: str):
        """
        Create a new card for the given user with the specified color.
        Input validation is handled by the serializer; this service handles the business logic.
        It calls the external provider, handles errors safely, and saves the card transactionally.
        """

        provider_external_id = user.external_id

        provider_client = BankProviderClient()
        try:
            provider_response = provider_client.create_card(provider_external_id, color)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 400:
                raise UserNotRegisteredError()
            elif exc.response.status_code >= 500:
                raise ProviderFailureError()
            else:
                # For other HTTP errors, raise a generic provider failure
                raise ProviderFailureError()
        except Exception as exc:
            # logger.error(f"Unexpected error during card creation: {exc}")
            raise ProviderFailureError()

        # Parse expiration_date as aware datetime
        expiration_date = provider_response.get("expiration_date")
        if expiration_date:
            try:
                dt = isoparse(expiration_date)
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                expiration_date = dt
                if expiration_date < timezone.now():
                    raise ValueError("Expiration date cannot be in the past.")
            except (ValueError, TypeError):
                raise InvalidCardDataError(detail={"error": "invalid_expiration_date", "message": "Provider returned an invalid expiration date."})
        
        # Enforce that 'status' is present in provider response
        if "status" not in provider_response:
            raise ProviderFailureError(detail={"error": "missing_status", "message": "Provider did not return a status."})

        # Transactional DB save
        try:
            with transaction.atomic():
                card = Card.objects.create(
                    user=user,
                    color=color,
                    external_id=provider_response.get("id"),
                    expiration_date=expiration_date,
                    status=provider_response["status"],
                )
        except Exception as exc:
            # logger.error(f"Database error during card creation: {exc}")
            raise RuntimeError("Failed to save card in the database.")

        return card

    @staticmethod
    def list_user_cards(user: CustomUser):
        """
        Return all cards belonging to the given user.
        """
        return Card.objects.filter(user=user)

    @staticmethod
    def retrieve_user_card(user: CustomUser, pk: int):
        """
        Retrieve a specific card by primary key, ensuring it belongs to the given user.
        Raises CardNotFoundError if not found.
        """
        try:
            return Card.objects.get(pk=pk, user=user)
        except Card.DoesNotExist:
            raise CardNotFoundError() 