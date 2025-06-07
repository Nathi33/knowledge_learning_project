from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from courses.models import Curriculum, Lesson
from core.models import AuditableMixin

class Payment(AuditableMixin, models.Model):
    """
    Model representing a payment made by a user for either a curriculum or a lesson.

    Attributes:
        user (ForeignKey): Reference to the user who made the payment. Can be null if the user is deleted.
        curriculum (ForeignKey): The purchased curriculum. Null if the payment is for a lesson.
        lesson (ForeignKey): The purchased lesson. Null if the payment is for a curriculum.
        amount (PositiveIntegerField): Amount paid in cents (e.g., 1999 for €19.99).
        timestamp (DateTimeField): The date and time the payment was made.
        status (CharField): The payment status. Possible values: 'paid' or 'failed'.
        stripe_checkout_id (CharField): Unique Stripe session ID associated with the payment.

    Validation:
        - A payment must be linked to either a curriculum or a lesson, but not both.
        - A payment must be linked to at least one (either curriculum or lesson).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    curriculum = models.ForeignKey(Curriculum, null=True, blank=True, on_delete=models.SET_NULL)
    lesson = models.ForeignKey(Lesson, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('paid', 'Payé'),
            ('failed', 'Échoué'),
        ],
        default='paid'
    )
    stripe_checkout_id = models.CharField(max_length=255, null=True, blank=True)

    def clean(self):
        super().clean()
        if self.curriculum and self.lesson:
            raise ValidationError("Un paiement ne peut concerner qu'un cursus OU une leçon, pas les deux.")
        if not self.curriculum and not self.lesson:
            raise ValidationError("Un paiement doit concerner soit un cursus, soit une leçon.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        user_display = f"{self.user.first_name} {self.user.last_name}" if self.user else "Utilisateur inconnu"
        if self.curriculum:
            return f"{user_display} - Cursus : {self.curriculum.title} - {self.amount}€"
        elif self.lesson:
            return f"{user_display} - Leçon : {self.lesson.title} - {self.amount}€"
        return f"{user_display} - Paiement invalide"


