from .models import Card
from users.models import CustomUser

class CardService:
    """
    Service layer for card-related business logic. Handles creation, retrieval, and integration with external providers.
    """
    @staticmethod
    def create_card(user: CustomUser, color: str) -> Card:
        """
        Create a new card for the given user with the specified color.
        (Implementation to be added in the next steps.)
        """
        pass 

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
        Raises Card.DoesNotExist if not found.
        """
        return Card.objects.get(pk=pk, user=user) 