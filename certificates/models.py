from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from courses.models import Theme
from core.models import AuditableMixin

class Certificate (AuditableMixin, models.Model):
    """
    Represents a certificate issued to a user for a specific theme.

    This certificate is valid only if the user has completed all lessons
    from the curriculums associated with the theme.

    Attributes:
        user (ForeignKey): The user to whom the certificate is issued.
        theme (ForeignKey): The theme corresponding to the certificate.
        issued_at (DateTimeField): Automatically set date and time when the certificate is issued.
        is_valid (BooleanField): Indicates whether the certificate is valid (default: True).

    Methods:
        clean(): Validates that the user is authenticated and has completed all
                 the required lessons to receive this certificate.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"Certificat {self.theme.name} - {self.user.first_name} {self.user.last_name}"

    def clean(self):
        """
        Validates the certificate's integrity before saving.

        Checks that:
        - The user is authenticated.
        - The user has completed all lessons in the curriculums related to the theme.

        Raises a ValidationError if these conditions are not met.
        """
        super().clean()
        # Verification that the user has completed all lessons in the curriculum
        curriculums = self.theme.curriculums.all()

        for curriculum in curriculums:
            lessons = curriculum.lessons.all()
            for lesson in lessons:
                if not lesson.is_completed_by_user(self.user):
                    raise ValidationError(
                        f"L'utilisateur {self.user.first_name} {self.user.last_name} n'a pas terminé la leçon '{lesson.title}' du cursus '{curriculum.title}'."
                    )
        if not self.user.is_authenticated:
            raise ValidationError("Le certificat doit être attribué à un utilisateur authentifié.")

