import pytest
from django.contrib.auth import get_user_model
from courses.models import Theme, Curriculum, Lesson, LessonCompletion

User = get_user_model()

@pytest.mark.django_db
def test_create_theme_curriculum_lesson():
    theme = Theme.objects.create(name="Informatique")
    curriculum = Curriculum.objects.create(theme=theme, title="Python Basics", price=100)
    lesson = Lesson.objects.create(curriculum=curriculum, title="Introduction", content="Contenu...", order=1, price=10)

    assert theme.pk is not None
    assert curriculum.pk is not None
    assert lesson.pk is not None
    assert str(theme) == "Informatique"
    assert str(curriculum) == "Python Basics - 100€"
    assert str(lesson) == "Leçon 1 : Introduction"


@pytest.mark.django_db
def test_lesson_completion_and_is_completed_by_user():
    user = User.objects.create_user(email="test@example.com", password="password123")
    theme = Theme.objects.create(name="Informatique")
    curriculum = Curriculum.objects.create(theme=theme, title="Python Basics", price=100)
    lesson = Lesson.objects.create(curriculum=curriculum, title="Intro", content="...", order=1, price=10)

    # Pas de completion pour l'instant
    assert lesson.is_completed_by_user(user) is False

    # Créer une completion non terminée
    LessonCompletion.objects.create(user=user, lesson=lesson, is_completed=False)
    assert lesson.is_completed_by_user(user) is False

    # Marquer comme terminée
    completion = LessonCompletion.objects.get(user=user, lesson=lesson)
    completion.is_completed = True
    completion.save()
    assert lesson.is_completed_by_user(user) is True


@pytest.mark.django_db
def test_theme_is_certified_by_user(monkeypatch):
    user = User.objects.create_user(email="test2@example.com", password="password123")
    theme = Theme.objects.create(name="Musique")
    curriculum = Curriculum.objects.create(theme=theme, title="Guitare", price=50)
    lesson1 = Lesson.objects.create(curriculum=curriculum, title="Accords", content="...", order=1, price=5)
    lesson2 = Lesson.objects.create(curriculum=curriculum, title="Rythme", content="...", order=2, price=5)

    # Patcher is_completed_by_user de Lesson pour simuler la complétion
    def fake_is_completed_by_user(self, user_arg):
        # Simule : la première leçon complétée, la deuxième pas
        return self.title == "Accords"

    monkeypatch.setattr(Lesson, "is_completed_by_user", fake_is_completed_by_user)

    assert theme.is_certified_by_user(user) is False

    # Modifier pour que toutes les leçons soient complétées
    def fake_is_completed_by_user_all(self, user_arg):
        return True

    monkeypatch.setattr(Lesson, "is_completed_by_user", fake_is_completed_by_user_all)

    assert theme.is_certified_by_user(user) is True
