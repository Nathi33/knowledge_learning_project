from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import AuditableMixin

class CustomUserManager(BaseUserManager):
    """
    Custom manager for the CustomUser model based on email authentication.

    Provides methods to create regular users and superusers without a username field,
    using only the email address for identification.
    """
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a user with the given email and password.

        Args:
            email (str): The user's email address.
            password (str, optional): The user's password.
            **extra_fields: Additional fields to be set on the user.

        Returns:
            CustomUser: The created user instance.

        Raises:
            ValueError: If no email is provided.
        """
        if not email:
            raise ValueError("L'adresse e-mail doit être fournie")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with administrative privileges.

        Args:
            email (str): The superuser's email address.
            password (str, optional): The superuser's password.
            **extra_fields: Additional fields to be set on the superuser.

        Returns:
            CustomUser: The created superuser instance.

        Raises:
            ValueError: If `is_staff` or `is_superuser` are not set to True.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser, AuditableMixin):
    """
    Custom user model that uses email instead of username for authentication.

    Includes additional fields such as `is_client`, `is_admin`, and `email_verified`.
    Inherits auditing features from AuditableMixin.
    """
    username = None
    email = models.EmailField(unique=True, verbose_name=_("Adresse e-mail"))
    last_name = models.CharField(max_length=30, verbose_name=_("Nom"))
    first_name = models.CharField(max_length=30, verbose_name=_("Prénom"))
    is_client = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['email']
