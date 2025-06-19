from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .models import Card
from .serializers import CardSerializer
from .services import CardService

class CardViewSet(viewsets.ViewSet):
    """API endpoint that allows cards to be viewed or edited."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Get all cards for the authenticated user using the service layer."""
        cards = CardService.list_user_cards(request.user)
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new card"""
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def retrieve(self, request, pk=None):
        """Get a specific card belonging to the authenticated user using the service layer. Ensures ownership and safe error handling."""
        try:
            card = CardService.retrieve_user_card(request.user, pk)
        except Card.DoesNotExist:
            return Response({'detail': 'Card not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            # Log the error internally (placeholder for actual logging)
            # logger.error(f"Error retrieving card: {exc}")
            return Response({'detail': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = CardSerializer(card)
        return Response(serializer.data)


