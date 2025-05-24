from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that authenticates users using their email address instead of username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user based on email and password.

        Args:
            request (HttpRequest): The current request instance.
            username (str): The email address of the user (passed as 'username' by Django auth system).
            password (str): The user's password.
            **kwargs: Additional keyword arguments.

        Returns:
            User instance if authentication is successful, otherwise None.
        """
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None