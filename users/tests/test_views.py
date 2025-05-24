from django.test import TestCase
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

@pytest.mark.django_db
def test_registration_user(client):
    """
    Test the user registration process.
    Checks that submitting the registration form creates an inactive user
    and redirects to the login page.
    """
    url = reverse('register')
    response = client.post(url, {
        'email': 'test@test.com',
        'first_name': 'Jane',
        'last_name': 'Doe',
        'password1': 'ComplexPassword123!',
        'password2': 'ComplexPassword123!',
    })
    assert response.status_code == 302
    assert response.url == reverse('login')
    assert User.objects.filter(email='test@test.com').exists()
    user = User.objects.get(email='test@test.com')
    # Inactive user before activation
    assert not user.is_active 

@pytest.mark.django_db
def test_account_activation(client):
    """
    Test the account activation flow.
    Verifies that accessing the activation link activates the user,
    redirects to home, and logs the user in.
    """
    user = User.objects.create_user(
        email='test@test.com',
        first_name='Jane',
        last_name='Doe',
        password='ComplexPassword123!',
        is_active=False,
    )

    # Generate activation link
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # Simulate the activation request
    url = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
    response = client.get(url)
    user.refresh_from_db()
    assert user.is_active
    assert response.status_code == 302
    assert response.url == reverse('home')

    # Verify that the user is now logged in
    session = client.session
    assert '_auth_user_id' in session
    assert str(user.pk) == session['_auth_user_id']

@pytest.mark.django_db
def test_login_success(client):
    """
    Test successful login with correct credentials.
    Verifies redirect to home and that the session contains the user's id.
    """
    # Create an active user
    user = User.objects.create_user(
        email = 'test@test.com',
        first_name = 'Jane',
        last_name = 'Doe',
        password='ComplexPassword123!',
        is_active=True,
    )

    login_url = reverse('login')
    response = client.post(login_url, {
        'username': 'test@test.com',
        'password': 'ComplexPassword123!',
    })

    assert response.status_code == 302
    assert response.url == reverse('home')

    session = client.session
    assert '_auth_user_id' in session
    assert str(user.pk) == session['_auth_user_id']

@pytest.mark.django_db
def test_registration_with_existing_email(client):
    """
    Test that registering with an already used email address
    returns the registration form with an email error.
    """
    User.objects.create_user(
        email='test@test.com',
        first_name='Jane',
        last_name='Doe',
        password='ComplexPassword123!',
        is_active=True
    )
    response = client.post(reverse('register'), {
        'email': 'test@test.com',
        'first_name': 'Jane',
        'last_name': 'Doe',
        'password1': 'ComplexPassword123!',
        'password2': 'ComplexPassword123!',
    })
    assert response.status_code == 200
    assert "form" in response.context
    assert "email" in response.context["form"].errors

