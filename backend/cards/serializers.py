from rest_framework import serializers
from .models import Card, CardChoices

class CardCreateSerializer(serializers.Serializer):
    """
    Serializer for card creation. Only requires the 'color'.
    Choices are sourced directly from the model to maintain a single source of truth.
    """
    color = serializers.ChoiceField(choices=CardChoices.Color.choices)


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'status', 'color', 'expiration_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'color', 'expiration_date', 'created_at', 'updated_at']
