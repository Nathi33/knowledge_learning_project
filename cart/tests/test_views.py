from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Lesson, Curriculum, Theme
from payments.models import Payment

User = get_user_model()

class CartViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="test@test.com", password="ComplexPassword123!")
        self.client.login(email="test@test.com", password="ComplexPassword123!")

        # Création d'un thème, d'un cursus et d'une leçon pour les tests
        self.theme = Theme.objects.create(name="Test Thème")
        self.curriculum = Curriculum.objects.create(theme=self.theme, title="Test Cursus", price=50)
        self.lesson = Lesson.objects.create(
            curriculum=self.curriculum,
            title="Test Leçon",
            price=20,
            order=1
        )

        self.add_to_cart_url_curriculum = reverse("add_to_cart", args=[self.curriculum.id, "curriculum"])
        self.add_to_cart_url_lesson = reverse("add_to_cart", args=[self.lesson.id, "lesson"])

    def test_add_to_cart_curriculum_success(self):
        response = self.client.post(self.add_to_cart_url_curriculum, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('L\'article a été ajouté au panier.', [m.message for m in response.context['messages']])
        session_cart = self.client.session['cart']
        self.assertEqual(len(session_cart), 1)
        self.assertEqual(session_cart[0]['type'], 'curriculum')
        self.assertEqual(session_cart[0]['id'], self.curriculum.id)
    
    def test_add_to_cart_lesson_success(self):
        response = self.client.post(self.add_to_cart_url_lesson, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('L\'article a été ajouté au panier.', [m.message for m in response.context['messages']])
        session_cart = self.client.session['cart']
        self.assertEqual(len(session_cart), 1)
        self.assertEqual(session_cart[0]['type'], 'lesson')
        self.assertEqual(session_cart[0]['id'], self.lesson.id)

    def test_cannot_add_curriculum_if_already_purchased(self):
        Payment.objects.create(user=self.user, curriculum=self.curriculum, amount=100, status='paid')

        response = self.client.post(self.add_to_cart_url_curriculum, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('Vous avez déjà acheté ce cursus.', [m.message for m in response.context['messages']])
        self.assertNotIn('cart', self.client.session)

    def test_cannot_add_lesson_if_already_purchased(self):
        Payment.objects.create(user=self.user, lesson=self.lesson, amount=20, status='paid')

        response = self.client.post(self.add_to_cart_url_lesson, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('Vous avez déjà acheté cette leçon.', [m.message for m in response.context['messages']])
        self.assertNotIn('cart', self.client.session)

    def test_cannot_add_lesson_if_curriculum_already_purchased(self):
        Payment.objects.create(user=self.user, curriculum=self.curriculum, amount=50, status='paid')

        response = self.client.post(self.add_to_cart_url_lesson, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('Vous avez déjà acheté le cursus complet de cette leçon. Vous ne pouvez pas acheter la leçon séparément.', [m.message for m in response.context['messages']])
        self.assertNotIn('cart', self.client.session)
    
    def test_cannot_add_curriculum_in_cart(self):
        session = self.client.session
        session['cart'] = [{'type': 'curriculum', 'id': self.curriculum.id, 'title': self.curriculum.title, 'price': self.curriculum.price, 'theme': self.theme.name}]
        session.save()

        response = self.client.post(self.add_to_cart_url_curriculum, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('Ce cursus est déjà dans votre panier.', [m.message for m in response.context['messages']])
        
    def test_cannot_add_lesson_if_curriculum_in_cart(self):
        session = self.client.session
        session['cart'] = [{'type': 'curriculum', 'id': self.curriculum.id, 'title': self.curriculum.title, 'price': self.curriculum.price, 'theme': self.theme.name}]
        session.save()

        response = self.client.post(self.add_to_cart_url_lesson, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('Le cursus de cette leçon est déjà dans votre panier. Vous ne pouvez pas acheter la leçon séparément.', [m.message for m in response.context['messages']])

    def test_invalid_item_type(self):
        url = reverse("add_to_cart", args=[self.curriculum.id, "invalid_type"])
        response = self.client.post(url, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('Type d\'article non valide.', [m.message for m in response.context['messages']])

    def test_remove_from_cart(self):
        session = self.client.session
        session['cart'] = [{'type': 'curriculum', 'id': self.curriculum.id, 'title': self.curriculum.title, 'price': self.curriculum.price, 'theme': self.theme.name}]
        session.save()

        url = reverse('remove_from_cart', args=[self.curriculum.id, 'curriculum'])
        response = self.client.get(url, follow=True)

        self.assertRedirects(response, reverse('cart'))
        self.assertIn('L\'article a été retiré du panier.', [m.message for m in response.context['messages']])
        self.assertEqual(len(self.client.session.get('cart', [])), 0)
