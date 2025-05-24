import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Lesson, Curriculum, Theme

User = get_user_model()

class PaymentViewTests(TestCase):
    def setUp(self):
        """
        Set up test data: user, theme, curriculum, lesson, and authenticated client session.
        """
        self.client = Client()
        self.user = User.objects.create_user(email='test@test.com', password='ComplexPassword123!')

        self.theme = Theme.objects.create(name="Test Thème")
        self.curriculum = Curriculum.objects.create(theme=self.theme, title="Test titre cursus", price=50)

        self.lesson = Lesson.objects.create(
            curriculum=self.curriculum,
            title="Test titre leçon", 
            price=20, 
            order=1
        )

        self.client.login(email='test@test.com', password='ComplexPassword123!')
        self.url = reverse('payments:checkout')

    def test_create_checkout_session_with_lesson(self):
        """
        Test that a checkout session is successfully created with a lesson in the cart.
        Expects a 200 response and a session ID in the JSON response.
        """
        session = self.client.session
        session['cart'] = [{'type': 'lesson', 'id': self.lesson.id, 'title': self.lesson.title, 'price': self.lesson.price}]
        session.save()

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json())
    
    def test_create_checkout_session_empty_cart(self):
        """
        Test that posting with an empty cart returns a 400 response with an error message.
        """
        session = self.client.session
        session['cart'] = []
        session.save()

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())