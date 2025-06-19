from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Card
from .serializers import CardSerializer

class CardViewSet(viewsets.ViewSet):
    """API endpoint that allows cards to be viewed or edited."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Get all cards for the authenticated user"""
        cards = Card.objects.filter(user=request.user)
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new card"""
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def retrieve(self, request, pk=None):
        """Get a specific card"""
        card = get_object_or_404(Card, pk=pk)
        serializer = CardSerializer(card)
        return Response(serializer.data)


