from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Lesson, Curriculum, Theme
from payments.models import Payment

User = get_user_model()

class CartViewsTests(TestCase):
    """
        Set up a user, theme, curriculum, and lesson for testing cart functionalities.
        """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="test@test.com", password="ComplexPassword123!")
        self.client.login(email="test@test.com", password="ComplexPassword123!")

        # Create test theme, curriculum and lesson
        self.theme = Theme.objects.create(name="Test Thème")
        self.curriculum = Curriculum.objects.create(theme=self.theme, title="Test Cursus", price=50)
        self.lesson = Lesson.objects.create(
            curriculum=self.curriculum,
            title="Test Leçon",
            price=20,
            order=1
        )

        # Prepare URLs for adding curriculum and lesson to cart
        self.add_to_cart_url_curriculum = reverse("add_to_cart", args=[self.curriculum.id, "curriculum"])
        self.add_to_cart_url_lesson = reverse("add_to_cart", args=[self.lesson.id, "lesson"])

    def test_add_to_cart_curriculum_success(self):
        """Test adding a curriculum to the cart successfully."""
        response = self.client.post(self.add_to_cart_url_curriculum, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('L\'article a été ajouté au panier.', [m.message for m in response.context['messages']])
        session_cart = self.client.session['cart']
        self.assertEqual(len(session_cart), 1)
        self.assertEqual(session_cart[0]['type'], 'curriculum')
        self.assertEqual(session_cart[0]['id'], self.curriculum.id)
    
    def test_add_to_cart_lesson_success(self):
        """Test adding a lesson to the cart successfully."""
        response = self.client.post(self.add_to_cart_url_lesson, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('L\'article a été ajouté au panier.', [m.message for m in response.context['messages']])
        session_cart = self.client.session['cart']
        self.assertEqual(len(session_cart), 1)
        self.assertEqual(session_cart[0]['type'], 'lesson')
        self.assertEqual(session_cart[0]['id'], self.lesson.id)

    def test_cannot_add_curriculum_if_already_purchased(self):
        """Test curriculum cannot be added if already purchased."""
        Payment.objects.create(user=self.user, curriculum=self.curriculum, amount=100, status='paid')

        response = self.client.post(self.add_to_cart_url_curriculum, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('Vous avez déjà acheté ce cursus.', [m.message for m in response.context['messages']])
        self.assertNotIn('cart', self.client.session)

    def test_cannot_add_lesson_if_already_purchased(self):
        """Test lesson cannot be added if already purchased."""
        Payment.objects.create(user=self.user, lesson=self.lesson, amount=20, status='paid')

        response = self.client.post(self.add_to_cart_url_lesson, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('Vous avez déjà acheté cette leçon.', [m.message for m in response.context['messages']])
        self.assertNotIn('cart', self.client.session)

    def test_cannot_add_lesson_if_curriculum_already_purchased(self):
        """Test lesson cannot be added if the whole curriculum has already been purchased."""
        Payment.objects.create(user=self.user, curriculum=self.curriculum, amount=50, status='paid')

        response = self.client.post(self.add_to_cart_url_lesson, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('Vous avez déjà acheté le cursus complet de cette leçon. Vous ne pouvez pas acheter la leçon séparément.', [m.message for m in response.context['messages']])
        self.assertNotIn('cart', self.client.session)
    
    def test_cannot_add_curriculum_in_cart(self):
        """Test curriculum cannot be added again if already in the cart."""
        session = self.client.session
        session['cart'] = [{'type': 'curriculum', 'id': self.curriculum.id, 'title': self.curriculum.title, 'price': self.curriculum.price, 'theme': self.theme.name}]
        session.save()

        response = self.client.post(self.add_to_cart_url_curriculum, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('Ce cursus est déjà dans votre panier.', [m.message for m in response.context['messages']])
        
    def test_cannot_add_lesson_if_curriculum_in_cart(self):
        """Test lesson cannot be added if its curriculum is already in the cart."""
        session = self.client.session
        session['cart'] = [{'type': 'curriculum', 'id': self.curriculum.id, 'title': self.curriculum.title, 'price': self.curriculum.price, 'theme': self.theme.name}]
        session.save()

        response = self.client.post(self.add_to_cart_url_lesson, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('Le cursus de cette leçon est déjà dans votre panier. Vous ne pouvez pas acheter la leçon séparément.', [m.message for m in response.context['messages']])

    def test_invalid_item_type(self):
        """Test handling of invalid item type."""
        url = reverse("add_to_cart", args=[self.curriculum.id, "invalid_type"])
        response = self.client.post(url, data={'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertIn('Type d\'article non valide.', [m.message for m in response.context['messages']])

    def test_remove_from_cart(self):
        """Test removing an item from the cart."""
        session = self.client.session
        session['cart'] = [{'type': 'curriculum', 'id': self.curriculum.id, 'title': self.curriculum.title, 'price': self.curriculum.price, 'theme': self.theme.name}]
        session.save()

        url = reverse('remove_from_cart', args=[self.curriculum.id, 'curriculum'])
        response = self.client.get(url, follow=True)

        self.assertRedirects(response, reverse('cart'))
        self.assertIn('L\'article a été retiré du panier.', [m.message for m in response.context['messages']])
        self.assertEqual(len(self.client.session.get('cart', [])), 0)
