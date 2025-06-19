from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import CustomUser as User


class CardChoices:
    # Choice classes

    class Color(models.TextChoices):
        BLACK = "black", _("Black")
        PINK = "pink", _("Pink")

    class Status(models.TextChoices):
        NOT_SUBMITTED = "not_submitted", _("Not Submitted")  # Not submitted to provider
        ORDERED = "ordered", _("Ordered")
        SENT = "sent", _("Sent")
        ACTIVATED = "activated", _("Activated")
        EXPIRED = "expired", _("Expired")
        OPPOSED = "opposed", _("Opposed")
        FAILED = "failed", _("Failed")
        DEACTIVATED = "deactivated", _("Deactivated")
        CANCELED = "canceled", _("Canceled")


class Card(models.Model):
    status = models.CharField(max_length=32, choices=CardChoices.Status.choices,
                              default=CardChoices.Status.NOT_SUBMITTED)
    external_id = models.CharField(max_length=120, null=True, blank=True)
    color = models.CharField(max_length=10, null=True, blank=True, choices=CardChoices.Color.choices)
    expiration_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.external_id

    class Meta:
        ordering = ['-created_at']
