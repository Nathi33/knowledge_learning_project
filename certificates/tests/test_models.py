from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from courses.models import Theme, Curriculum, Lesson, LessonCompletion
from certificates.models import Certificate

User = get_user_model()

class CertificateModelTests(TestCase):
    def setUp(self):
        """
        Set up a test user, theme, curriculum, and associated lessons.
        """
        self.user = User.objects.create_user(
            email='test@test.com', 
            password='ComplexPassword123!', 
            first_name='Jane', 
            last_name='Doe',
            is_active=True
        )
        
        # Create a theme
        self.theme = Theme.objects.create(name="Test Thème")
        
        # Create a curriculum linked to the theme
        self.curriculum = Curriculum.objects.create(theme=self.theme, title="Test titre cursus", price=100)
        
        # Create lessons linked to the curriculum
        self.lesson1 = Lesson.objects.create(
            curriculum=self.curriculum, title="Test titre leçon 1", order=1, price=0, content="Contenu test 1"
        )
        self.lesson2 = Lesson.objects.create(
            curriculum=self.curriculum, title="Test titre leçon 2", order=2, price=0, content="Contenu test 2"
        )
    
    def test_certificate_clean_fails_if_lessons_not_completed(self):
        """
        Test that certificate validation fails if not all lessons are completed.
        """
        cert = Certificate(user=self.user, theme=self.theme)
        with self.assertRaises(ValidationError) as cm:
            cert.clean()
        self.assertIn("n'a pas terminé la leçon", str(cm.exception))
    
    def test_certificate_clean_passes_if_all_lessons_completed(self):
        """
        Test that certificate validation passes if all lessons are marked as completed.
        """
        LessonCompletion.objects.create(user=self.user, lesson=self.lesson1, is_completed=True)
        LessonCompletion.objects.create(user=self.user, lesson=self.lesson2, is_completed=True)
        
        cert = Certificate(user=self.user, theme=self.theme)
        
        # Should not raise ValidationError
        try:
            cert.clean()
        except ValidationError:
            self.fail("clean() a levé ValidationError alors que toutes les leçons sont terminées")
    
    def test_certificate_str_method(self):
        """
        Test the string representation of the Certificate model.
        """
        cert = Certificate.objects.create(user=self.user, theme=self.theme)
        self.assertEqual(str(cert), f"Certificat {self.theme.name} - {self.user.first_name} {self.user.last_name}")
