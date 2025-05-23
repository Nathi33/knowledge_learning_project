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
    url = reverse('register')
    response = client.post(url, {
        'email': 'test@example.com',
        'first_name': 'Jane',
        'last_name': 'Test',
        'password1': 'ComplexPassword123!',
        'password2': 'ComplexPassword123!',
    })
    assert response.status_code == 302
    assert response.url == reverse('login')
    assert User.objects.filter(email='test@example.com').exists()
    user = User.objects.get(email='test@example.com')
    assert not user.is_active  # utilisateur inactif avant activation

@pytest.mark.django_db
def test_account_activation(client):
    user = User.objects.create_user(
        email='testactivate@example.com',
        first_name='Jane',
        last_name='Test',
        password='ComplexPassword123!',
        is_active=False,
    )

    # Générer le lien d'activation
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # Simuler la requête d'activation
    url = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
    response = client.get(url)
    user.refresh_from_db()
    assert user.is_active
    assert response.status_code == 302
    assert response.url == reverse('home')

    # Vérifier que l'utilisateur est maintenant connecté
    session = client.session
    assert '_auth_user_id' in session
    assert str(user.pk) == session['_auth_user_id']

@pytest.mark.django_db
def test_login_success(client):
    # Créer un utilisateur actif
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
