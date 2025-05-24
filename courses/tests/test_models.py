import pytest
from django.contrib.auth import get_user_model
from courses.models import Theme, Curriculum, Lesson, LessonCompletion

User = get_user_model()

@pytest.mark.django_db
def test_create_theme_curriculum_lesson():
    """
    Test the creation of a Theme, Curriculum, and Lesson,
    and verify their string representations.
    """
    theme = Theme.objects.create(name="Test thème")
    curriculum = Curriculum.objects.create(theme=theme, title="Test titre cursus", price=50)
    lesson = Lesson.objects.create(curriculum=curriculum, title="Test titre leçon", content="Contenu test", order=1, price=20)

    assert theme.pk is not None
    assert curriculum.pk is not None
    assert lesson.pk is not None
    assert str(theme) == "Test thème"
    assert str(curriculum) == "Test titre cursus - 50€"
    assert str(lesson) == "Leçon 1 : Test titre leçon"


@pytest.mark.django_db
def test_lesson_completion_and_is_completed_by_user():
    """
    Test the behavior of is_completed_by_user method for a Lesson.
    """
    user = User.objects.create_user(email="test@test.com", password="ComplexPassword123!")
    theme = Theme.objects.create(name="Test thème")
    curriculum = Curriculum.objects.create(theme=theme, title="Test titre cursus", price=50)
    lesson = Lesson.objects.create(curriculum=curriculum, title="Test titre leçon", content="...", order=1, price=20)

    # No completion yet
    assert lesson.is_completed_by_user(user) is False

    # Create a LessonCompletion not marked as completed
    LessonCompletion.objects.create(user=user, lesson=lesson, is_completed=False)
    assert lesson.is_completed_by_user(user) is False

    # Mark as completed
    completion = LessonCompletion.objects.get(user=user, lesson=lesson)
    completion.is_completed = True
    completion.save()
    assert lesson.is_completed_by_user(user) is True


@pytest.mark.django_db
def test_theme_is_certified_by_user(monkeypatch):
    """
    Test the is_certified_by_user method of Theme using monkeypatching
    to simulate lesson completion scenarios.
    """
    user = User.objects.create_user(email="test@test.com", password="ComplexPassword123!")
    theme = Theme.objects.create(name="Test thème")
    curriculum = Curriculum.objects.create(theme=theme, title="Test titre cursus", price=50)
    lesson1 = Lesson.objects.create(curriculum=curriculum, title="Test titre leçon 1", content="...", order=1, price=20)
    lesson2 = Lesson.objects.create(curriculum=curriculum, title="Test titre leçon 2", content="...", order=2, price=20)

    # Simulate firts lesson completed, second not completed
    def fake_is_completed_by_user(self, user_arg):
        # Simule : la première leçon complétée, la deuxième pas
        return self.title == "Test titre leçon 1"

    monkeypatch.setattr(Lesson, "is_completed_by_user", fake_is_completed_by_user)

    assert theme.is_certified_by_user(user) is False

    # Simulate all lessons completed
    def fake_is_completed_by_user_all(self, user_arg):
        return True

    monkeypatch.setattr(Lesson, "is_completed_by_user", fake_is_completed_by_user_all)

    assert theme.is_certified_by_user(user) is True
