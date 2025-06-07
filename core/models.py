from django.db import models
from django.conf import settings
from core.middleware import get_current_user
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render

class TimeStampeMixin(models.Model):
    """
    Abstract base model that adds timestamp fields to track creation and update times.

    Fields:
        created_at (DateTimeField): Automatically set to the current datetime when the object is created.
        updated_at (DateTimeField): Automatically updated to the current datetime each time the object is saved.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        abstract = True


class AuditableMixin(TimeStampeMixin):
    """
    Abstract base model that adds user tracking fields to log which user created or last modified the object.

    Inherits from:
        TimeStampeMixin: Provides created_at and updated_at fields.

    Fields:
        created_by (ForeignKey): The user who created the object.
        updated_by (ForeignKey): The user who last modified the object.

    Methods:
        save(): Overrides the default save method to automatically populate
                created_by and updated_by based on the current user.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True,
        blank=True, 
        related_name='%(class)s_created_by', 
        on_delete=models.SET_NULL,
        verbose_name="Créé par"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True,
        blank=True,
        related_name='%(class)s_updated_by', 
        on_delete=models.SET_NULL,
        verbose_name="Mis à jour par"
        )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to automatically assign
        the current user to created_by and updated_by fields.
        """
        user = get_current_user()
        if user and not isinstance(user, AnonymousUser):
            if not self.pk and not self.created_by:
                self.created_by = user
            self.updated_by = user
        super().save(*args, **kwargs)

