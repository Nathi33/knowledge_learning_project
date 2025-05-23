import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Lesson, Curriculum, Theme

User = get_user_model()

class PaymentViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@test.com', password='ComplexPassword123!')

        self.theme = Theme.objects.create(name="Test Thème")
        self.curriculum = Curriculum.objects.create(theme=self.theme, title="Test Cursus", price=50)

        self.lesson = Lesson.objects.create(
            curriculum=self.curriculum,
            title="Test Leçon", 
            price=20, 
            order=1
        )

        self.client.login(email='test@test.com', password='ComplexPassword123!')
        self.url = reverse('payments:checkout')

    def test_create_checkout_session_with_lesson(self):
        session = self.client.session
        session['cart'] = [{'type': 'lesson', 'id': self.lesson.id, 'title': self.lesson.title, 'price': self.lesson.price}]
        session.save()

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json())
    
    def test_create_checkout_session_empty_cart(self):
        session = self.client.session
        session['cart'] = []
        session.save()

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())