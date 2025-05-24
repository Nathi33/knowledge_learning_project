import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Lesson, Curriculum, Theme, LessonCompletion
from certificates.models import Certificate
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

User = get_user_model()

@pytest.mark.django_db
def test_view_certificate_user_not_authenticated():
    """
    Test that an unauthenticated user is redirected when trying to access the certificate view.
    """
    # Create a test user
    user = User.objects.create_user(email='test@test.com', password='ComplexPassword123!')

    # Create a test theme
    theme = Theme.objects.create(name="Test Theme", updated_by=user)

    client = Client()
    url = reverse('view_certificate', args=[theme.id])

    # Make a GET request without being logged in
    response = client.get(url)

    # Expect a redirect to the login page
    assert response.status_code == 302
    assert '/accounts/login/' in response.url or '/login/' in response.url



