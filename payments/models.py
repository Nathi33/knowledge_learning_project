from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from courses.models import Curriculum, Lesson

class Payment(models.Model):
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
        if self.curriculum:
            return f"{self.user.username} - Cursus : {self.curriculum.title} - {self.amount}€"
        elif self.lesson:
            return f"{self.user.username} - Leçon : {self.lesson.title} - {self.amount}€"
        return f"{self.user.username} - Paiement invalide"


