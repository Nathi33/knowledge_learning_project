from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from courses.models import Theme, Curriculum, Lesson, LessonCompletion
from certificates.models import Certificate

User = get_user_model()

class CertificateModelTests(TestCase):

    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            email='test@example.com', 
            password='password123', 
            first_name='Jean', 
            last_name='Dupont',
            is_active=True
        )
        
        # Créer un thème
        self.theme = Theme.objects.create(name="Informatique")
        
        # Créer un cursus lié au thème
        self.curriculum = Curriculum.objects.create(theme=self.theme, title="Python avancé", price=100)
        
        # Créer des leçons liées au cursus
        self.lesson1 = Lesson.objects.create(
            curriculum=self.curriculum, title="Les bases", order=1, price=0, content="Contenu 1"
        )
        self.lesson2 = Lesson.objects.create(
            curriculum=self.curriculum, title="Les fonctions", order=2, price=0, content="Contenu 2"
        )
    
    def test_certificate_clean_fails_if_lessons_not_completed(self):
        # Aucune leçon terminée par l'utilisateur
        cert = Certificate(user=self.user, theme=self.theme)
        with self.assertRaises(ValidationError) as cm:
            cert.clean()
        self.assertIn("n'a pas terminé la leçon 'Les bases'", str(cm.exception))
    
    def test_certificate_clean_passes_if_all_lessons_completed(self):
        # Marquer toutes les leçons comme terminées pour l'utilisateur
        LessonCompletion.objects.create(user=self.user, lesson=self.lesson1, is_completed=True)
        LessonCompletion.objects.create(user=self.user, lesson=self.lesson2, is_completed=True)
        
        cert = Certificate(user=self.user, theme=self.theme)
        
        # Ne doit pas lever d'exception
        try:
            cert.clean()
        except ValidationError:
            self.fail("clean() a levé ValidationError alors que toutes les leçons sont terminées")
    
    def test_certificate_str_method(self):
        cert = Certificate.objects.create(user=self.user, theme=self.theme)
        self.assertEqual(str(cert), f"Certificat {self.theme.name} - {self.user.first_name} {self.user.last_name}")
