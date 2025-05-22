from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from courses.models import Curriculum, Theme

class Certificate (models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"Certificat {self.theme.name} - {self.user.username}"

    def clean(self):
        super().clean()
        # Vérification que l'utilisateur a terminé toutes les leçons du cursus
        curriculums = self.theme.curriculums.all()

        for curriculum in curriculums:
            lessons = curriculum.lessons.all()
            for lesson in lessons:
                if not lesson.is_completed_by_user(self.user):
                    raise ValidationError(
                        f"L'utilisateur {self.user.username} n'a pas terminé la leçon '{lesson.title}' du cursus '{curriculum.title}'."
                    )
        if not self.user.is_authenticated:
            raise ValidationError("Le certificat doit être attribué à un utilisateur authentifié.")

