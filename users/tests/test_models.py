import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_user_success():
    """
    Test successful creation of a regular user with valid email,
    password, first name, and last name.
    Checks attributes and string representation.
    """
    user = User.objects.create_user(
        email="test@test.com",
        password="ComplexPassword123!",
        first_name="Jane",
        last_name="Doe"
    )
    assert user.email == "test@test.com"
    assert user.first_name == "Jane"
    assert user.last_name == "Doe"
    assert user.check_password("ComplexPassword123!")
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser
    assert user.__str__() == "Jane Doe"


@pytest.mark.django_db
def test_create_user_without_email_raises():
    """
    Test that creating a user without an email raises a ValueError
    with the message indicating email must be provided.
    """
    with pytest.raises(ValueError) as excinfo:
        User.objects.create_user(
            email="",
            password="ComplexPassword123!",
            first_name="Jane",
            last_name="Doe"
        )
    assert "e-mail doit être fournie" in str(excinfo.value)


@pytest.mark.django_db
def test_create_superuser_success():
    """
    Test successful creation of a superuser with required fields.
    Checks that is_staff and is_superuser are True.
    """
    superuser = User.objects.create_superuser(
        email="admin@test.com",
        password="AdminPassword123!",
        first_name="Admin",
        last_name="Test"
    )
    assert superuser.email == "admin@test.com"
    assert superuser.is_staff is True
    assert superuser.is_superuser is True
    assert superuser.is_active is True
    assert superuser.__str__() == "Admin Test"


@pytest.mark.django_db
def test_create_superuser_without_is_staff_raises():
    """
    Test that creating a superuser with is_staff=False raises a ValueError
    indicating is_staff must be True for superusers.
    """
    with pytest.raises(ValueError) as excinfo:
        User.objects.create_superuser(
            email="admin@test.com",
            password="AdminPassword123!",
            first_name="Admin",
            last_name="Test",
            is_staff=False
        )
    assert "doit avoir is_staff=True" in str(excinfo.value)


@pytest.mark.django_db
def test_create_superuser_without_is_superuser_raises():
    """
    Test that creating a superuser with is_superuser=False raises a ValueError
    indicating is_superuser must be True for superusers.
    """
    with pytest.raises(ValueError) as excinfo:
        User.objects.create_superuser(
            email="admin@test.com",
            password="AdminPassword123!",
            first_name="Admin",
            last_name="Test",
            is_superuser=False
        )
    assert "doit avoir is_superuser=True" in str(excinfo.value)
