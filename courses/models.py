from django.conf import settings
from django.db import models

class Theme(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Curriculum(models.Model):
    theme = models.ForeignKey('Theme', on_delete=models.CASCADE, related_name='curriculums')
    title = models.CharField(max_length=150)
    price = models.PositiveIntegerField()

    def is_paid_by_user(self, user):
        from payments.models import Payment
        return Payment.objects.filter(user=user, curriculum=self, status='paid').exists()

    def __str__(self):
        return f"{self.title} - {self.price}€"


class Lesson(models.Model):
    curriculum = models.ForeignKey('Curriculum', on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=150)
    content = models.TextField()
    order = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    is_validated = models.BooleanField(default=False)
    video_url = models.URLField(null=True, blank=True)

    def is_completed_by_user(self, user):
        try:
            completion = LessonCompletion.objects.get(user=user, lesson=self)
            return completion.is_completed
        except LessonCompletion.DoesNotExist:
            return False

    def is_paid_by_user(self, user):
        from payments.models import Payment
        return Payment.objects.filter(user=user, lesson=self, status='paid').exists()

    def __str__(self):
        return f"Leçon {self.order} : {self.title}"


class LessonCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - Terminé: {self.is_completed}"