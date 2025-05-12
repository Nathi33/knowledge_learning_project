from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    username = None  # Supprimer le champ username
    email = models.EmailField(unique=True, verbose_name=_("Adresse e-mail"))
    last_name = models.CharField(max_length=30, verbose_name=_("Nom"))
    first_name = models.CharField(max_length=30, verbose_name=_("Prénom"))
    is_client = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['email']
