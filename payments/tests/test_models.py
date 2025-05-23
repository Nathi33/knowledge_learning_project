import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from courses.models import Curriculum, Lesson, Theme
from payments.models import Payment

User = get_user_model()

@pytest.mark.django_db
def test_create_payment_curriculum():
    user = User.objects.create_user(email="user1@example.com", password="password123")
    theme = Theme.objects.create(name="Test Theme")
    curriculum = Curriculum.objects.create(theme=theme, title="Test Curriculum", price=100)

    payment = Payment(user=user, curriculum=curriculum, amount=100, status='paid')
    payment.full_clean()  # Validation manuelle
    payment.save()

    assert payment.pk is not None
    assert str(payment) == f"{user.first_name} {user.last_name} - Cursus : {curriculum.title} - 100€"


@pytest.mark.django_db
def test_create_payment_lesson():
    user = User.objects.create_user(email="user2@example.com", password="password123")
    theme = Theme.objects.create(name="Theme 2")
    curriculum = Curriculum.objects.create(theme=theme, title="Curriculum 2", price=200)
    lesson = Lesson.objects.create(curriculum=curriculum, title="Lesson 1", content="...", order=1, price=20)

    payment = Payment(user=user, lesson=lesson, amount=20, status='paid')
    payment.full_clean()
    payment.save()

    assert payment.pk is not None
    assert str(payment) == f"{user.first_name} {user.last_name} - Leçon : {lesson.title} - 20€"


@pytest.mark.django_db
def test_payment_validation_error_both_curriculum_and_lesson():
    user = User.objects.create_user(email="user3@example.com", password="password123")
    theme = Theme.objects.create(name="Theme 3")
    curriculum = Curriculum.objects.create(theme=theme, title="Curriculum 3", price=300)
    lesson = Lesson.objects.create(curriculum=curriculum, title="Lesson 2", content="...", order=2, price=30)

    payment = Payment(user=user, curriculum=curriculum, lesson=lesson, amount=330, status='paid')

    with pytest.raises(ValidationError) as excinfo:
        payment.full_clean()
    assert "qu'un cursus OU une leçon" in str(excinfo.value)


@pytest.mark.django_db
def test_payment_validation_error_neither_curriculum_nor_lesson():
    user = User.objects.create_user(email="user4@example.com", password="password123")

    payment = Payment(user=user, amount=50, status='paid')

    with pytest.raises(ValidationError) as excinfo:
        payment.full_clean()
    assert "soit un cursus, soit une leçon" in str(excinfo.value)


@pytest.mark.django_db
def test_str_unknown_user_and_invalid_payment():
    # Cas où user est None
    payment = Payment(user=None, amount=10, status='paid')

    # Payment invalide (ni curriculum ni lesson) -> on force save avec patch pour éviter clean
    with pytest.raises(ValidationError):
        payment.full_clean()

    # Forcer création en ignorant la validation (pas recommandé dans la vraie vie, juste pour test __str__)
    payment = Payment(amount=10)
    payment.user = None

    # __str__ doit retourner "Utilisateur inconnu - Paiement invalide"
    assert str(payment) == "Utilisateur inconnu - Paiement invalide"
