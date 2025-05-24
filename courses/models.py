from django.conf import settings
from django.db import models
from core.models import AuditableMixin

class Theme(AuditableMixin, models.Model):
    """
    Represents a course theme grouping multiple curriculums.

    Attributes:
        name (str): Unique name of the theme.

    Methods:
        is_certified_by_user(user): Checks if the user has completed all lessons in the theme.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    def is_certified_by_user(self, user):
        """
        Check if the given user has completed all lessons in all curriculums of this theme.

        Args:
            user (User): The user to check completion status for.

        Returns:
            bool: True if all lessons are completed by the user, False otherwise.
        """
        for curriculum in self.curriculums.all():
            for lesson in curriculum.lessons.all():
                if not lesson.is_completed_by_user(user):
                    return False
        return True


class Curriculum(AuditableMixin, models.Model):
    """
    Represents a curriculum consisting of a collection of lessons within a theme.

    Attributes:
        theme (Theme): ForeignKey to the Theme it belongs to.
        title (str): Title of the curriculum.
        price (int): Price in euros.

    Methods:
        is_paid_by_user(user): Checks if the user has paid for this curriculum.
    """
    theme = models.ForeignKey('Theme', on_delete=models.CASCADE, related_name='curriculums')
    title = models.CharField(max_length=150)
    price = models.PositiveIntegerField()

    def is_paid_by_user(self, user):
        """
        Check if the user has paid for this curriculum.

        Args:
            user (User): The user to check payment status for.

        Returns:
            bool: True if the user has a paid payment record for this curriculum, False otherwise.
        """
        from payments.models import Payment
        return Payment.objects.filter(user=user, curriculum=self, status='paid').exists()

    def __str__(self):
        return f"{self.title} - {self.price}€"


class Lesson(AuditableMixin, models.Model):
    """
    Represents an individual lesson within a curriculum.

    Attributes:
        curriculum (Curriculum): ForeignKey to the Curriculum it belongs to.
        title (str): Title of the lesson.
        content (str): Text content of the lesson.
        order (int): Order of the lesson within the curriculum.
        price (int): Price in euros for this lesson.
        is_validated (bool): Flag indicating if the lesson is validated.
        video_url (str or None): Optional URL for an associated video.

    Methods:
        is_completed_by_user(user): Checks if the user has completed this lesson.
        is_paid_by_user(user): Checks if the user has paid for this lesson.
    """
    curriculum = models.ForeignKey('Curriculum', on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=150)
    content = models.TextField()
    order = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    is_validated = models.BooleanField(default=False)
    video_url = models.URLField(null=True, blank=True)

    def is_completed_by_user(self, user):
        """
        Check if the user has paid for this lesson.

        Args:
            user (User): The user to check payment status for.

        Returns:
            bool: True if the user has a paid payment record for this lesson, False otherwise.
        """
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


class LessonCompletion(AuditableMixin, models.Model):
    """
    Tracks the completion status of a lesson for a user.

    Attributes:
        user (User): The user who completed the lesson.
        lesson (Lesson): The lesson being completed.
        is_completed (bool): Whether the lesson is completed.
        completed_at (datetime or None): Date and time when the lesson was completed.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.lesson.title} - Terminé: {self.is_completed}"