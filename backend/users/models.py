from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """Custom User model with external_id field"""
    external_id = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name=_('External ID'),
        help_text=_('External identifier for the user in external systems')
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username
