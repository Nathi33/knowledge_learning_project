import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_user_success():
    user = User.objects.create_user(
        email="testuser@example.com",
        password="strongpassword123",
        first_name="Test",
        last_name="User"
    )
    assert user.email == "testuser@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.check_password("strongpassword123")
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser
    assert user.__str__() == "Test User"


@pytest.mark.django_db
def test_create_user_without_email_raises():
    with pytest.raises(ValueError) as excinfo:
        User.objects.create_user(
            email="",
            password="pass",
            first_name="No",
            last_name="Email"
        )
    assert "e-mail doit être fournie" in str(excinfo.value)


@pytest.mark.django_db
def test_create_superuser_success():
    superuser = User.objects.create_superuser(
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User"
    )
    assert superuser.email == "admin@example.com"
    assert superuser.is_staff is True
    assert superuser.is_superuser is True
    assert superuser.is_active is True
    assert superuser.__str__() == "Admin User"


@pytest.mark.django_db
def test_create_superuser_without_is_staff_raises():
    with pytest.raises(ValueError) as excinfo:
        User.objects.create_superuser(
            email="admin2@example.com",
            password="adminpass",
            first_name="Admin2",
            last_name="User2",
            is_staff=False
        )
    assert "doit avoir is_staff=True" in str(excinfo.value)


@pytest.mark.django_db
def test_create_superuser_without_is_superuser_raises():
    with pytest.raises(ValueError) as excinfo:
        User.objects.create_superuser(
            email="admin3@example.com",
            password="adminpass",
            first_name="Admin3",
            last_name="User3",
            is_superuser=False
        )
    assert "doit avoir is_superuser=True" in str(excinfo.value)
