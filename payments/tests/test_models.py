import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from courses.models import Curriculum, Lesson, Theme
from payments.models import Payment

User = get_user_model()

@pytest.mark.django_db
def test_create_payment_curriculum():
    """
    Test creating a payment linked to a curriculum.
    Ensures the payment is validated, saved, and string representation is correct.
    """
    user = User.objects.create_user(email="test@test.com", password="ComplexPassword123!")
    theme = Theme.objects.create(name="Test Theme")
    curriculum = Curriculum.objects.create(theme=theme, title="Test titre curriculum", price=50)

    payment = Payment(user=user, curriculum=curriculum, amount=50, status='paid')
    # Manual validation
    payment.full_clean() 
    payment.save()

    assert payment.pk is not None
    assert str(payment) == f"{user.first_name} {user.last_name} - Cursus : {curriculum.title} - 50€"


@pytest.mark.django_db
def test_create_payment_lesson():
    """
    Test creating a payment linked to a lesson.
    Ensures the payment is validated, saved, and string representation is correct.
    """
    user = User.objects.create_user(email="test@test.com", password="ComplexPassword123!")
    theme = Theme.objects.create(name="Test Theme")
    curriculum = Curriculum.objects.create(theme=theme, title="Test titre cursus", price=50)
    lesson = Lesson.objects.create(curriculum=curriculum, title="Test titre leçon", content="...", order=1, price=20)

    payment = Payment(user=user, lesson=lesson, amount=20, status='paid')
    payment.full_clean()
    payment.save()

    assert payment.pk is not None
    assert str(payment) == f"{user.first_name} {user.last_name} - Leçon : {lesson.title} - 20€"


@pytest.mark.django_db
def test_payment_validation_error_both_curriculum_and_lesson():
    """
    Test that a payment cannot be linked to both a curriculum and a lesson at the same time.
    Expects a ValidationError.
    """
    user = User.objects.create_user(email="test@test.com", password="ComplexPassword123!")
    theme = Theme.objects.create(name="Test Theme")
    curriculum = Curriculum.objects.create(theme=theme, title="Test titre cursus", price=50)
    lesson = Lesson.objects.create(curriculum=curriculum, title="Test titre leçon", content="...", order=2, price=20)

    payment = Payment(user=user, curriculum=curriculum, lesson=lesson, amount=70, status='paid')

    with pytest.raises(ValidationError) as excinfo:
        payment.full_clean()
    assert "qu'un cursus OU une leçon" in str(excinfo.value)


@pytest.mark.django_db
def test_payment_validation_error_neither_curriculum_nor_lesson():
    """
    Test that a payment must be linked to either a curriculum or a lesson.
    Expects a ValidationError when neither is set.
    """
    user = User.objects.create_user(email="test@test.com", password="ComplexPassword123!")

    payment = Payment(user=user, amount=50, status='paid')

    with pytest.raises(ValidationError) as excinfo:
        payment.full_clean()
    assert "soit un cursus, soit une leçon" in str(excinfo.value)


@pytest.mark.django_db
def test_str_unknown_user_and_invalid_payment():
    """
    Test __str__ method behavior when the user is None and the payment is invalid.
    Ensures fallback string is used.
    """
    # User is None and payment is invalid (neither curriculum nor lesson)
    payment = Payment(user=None, amount=10, status='paid')
    with pytest.raises(ValidationError):
        payment.full_clean()

    # Bypass validation for test purposes only
    payment = Payment(amount=10)
    payment.user = None

    #  __str__ should return fallback string for unknown user and invalid payment
    assert str(payment) == "Utilisateur inconnu - Paiement invalide"
