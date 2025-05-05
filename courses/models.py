from django.db import models

class Theme(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Curriculum(models.Model):
    theme = models.ForeignKey('Theme', on_delete=models.CASCADE, related_name='curriculums')
    title = models.CharField(max_length=150)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} - {self.price}€"

class Lesson(models.Model):
    curriculum = models.ForeignKey('Curriculum', on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=150)
    content = models.TextField()
    order = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    is_validated = models.BooleanField(default=False)

    def __str__(self):
        return f"Leçon {self.order} : {self.title}"