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
    theme = Theme.objects.create(name="Test Theme")

    client = Client()

    url = reverse('view_certificate', args=[theme.id])
    response = client.get(url)

    assert response.status_code == 302
    assert '/accounts/login/' in response.url or '/login/' in response.url

