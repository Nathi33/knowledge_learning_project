import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Lesson, Curriculum, Theme, LessonCompletion

User = get_user_model()

class CoursesViewsTests(TestCase):
    def setUp(self):
        """
        Create a test user, theme, curriculum and lesson before each test.
        """
        self.client = Client()
        self.user = User.objects.create_user(email="test@test.com", password="ComplexPassword123!")
        self.theme = Theme.objects.create(name="Test Thème")
        self.curriculum = Curriculum.objects.create(theme=self.theme, title="Test Cursus", price=50)
        self.lesson = Lesson.objects.create(
            curriculum=self.curriculum,
            title="Test Leçon",
            content="Contenu test de la leçon",
            price=20,
            order=1
        )

    def test_theme_detail_view(self):
        """
        Ensure the theme detail view displays the curriculum title.
        """
        url = reverse('theme_detail', args=[self.theme.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.curriculum.title)

    def test_curriculum_detail_view(self):
        """
        Ensure the curriculum detail view displays the lesson title.
        """
        url = reverse('curriculum_detail', args=[self.curriculum.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lesson.title)

    def test_complete_lesson_post(self):
        """
        Test completing a lesson via POST request after simulating a paid lesson.
        """
        self.client.login(email="test@test.com", password="ComplexPassword123!")

        # Simulate a payment for the lesson
        from payments.models import Payment
        Payment.objects.create(user=self.user, lesson=self.lesson, amount=self.lesson.price, status='paid')

        url = reverse('complete_lesson', args=[self.lesson.id])
        response = self.client.post(url)

        # Check redirection to dashboard
        self.assertRedirects(response, reverse('dashboard'))

        # Check that the lesson is marked as completed
        self.assertTrue(LessonCompletion.objects.filter(user=self.user, lesson=self.lesson, is_completed=True).exists())