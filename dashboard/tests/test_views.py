import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Theme, Curriculum, Lesson, LessonCompletion
from payments.models import Payment

User = get_user_model()

@pytest.mark.django_db
def test_dashboard_requires_login(client):
    """
    Test that the dashboard view requires authentication.
    """
    url = reverse('dashboard')
    response = client.get(url)
    # Ensure redirection to login occurs
    assert response.status_code == 302
    assert '/login/' in response.url

@pytest.mark.django_db
def test_dashboard_empty_data(client):
    """
    Test dashboard with no purchased curriculum or standalone lessons.
    """
    user = User.objects.create_user(email='test@test.com', password='ComplexPassword123!')
    client.login(email='test@test.com', password='ComplexPassword123!')

    url = reverse('dashboard')
    response = client.get(url)

    assert response.status_code == 200
    # No curriculum should be displayed
    assert b'No curriculum' not in response.content 
    # Context variables should be empty or properly initialized
    assert response.context['theme_with_curriculums'] == []
    assert response.context['standalone_lessons_by_theme'] == {}

@pytest.mark.django_db
def test_dashboard_with_purchased_curriculum(client):
    """
    Test dashboard when a curriculum has been purchased by the user.
    """
    user = User.objects.create_user(email='test@test.com', password='ComplexPassword123!')
    theme = Theme.objects.create(name='Test Thème')
    curriculum = Curriculum.objects.create(title='Test titre cursus', theme=theme, price=50)
    lesson1 = Lesson.objects.create(title='Test titre leçon 1', curriculum=curriculum, order=1, price=0)
    lesson2 = Lesson.objects.create(title='Test titre leçon 2', curriculum=curriculum, order=2, price=0)

    # Create a payment for the curriculum
    Payment.objects.create(user=user, curriculum=curriculum, amount=curriculum.price, status='paid')

    client.login(email='test@test.com', password='ComplexPassword123!')
    url = reverse('dashboard')
    response = client.get(url)

    assert response.status_code == 200

    # Theme should be present in the context
    themes = [item['theme'] for item in response.context['theme_with_curriculums']]
    assert theme in themes

    # Curriculum should be marked as purchased
    curriculum_data = response.context['theme_with_curriculums'][0]['curriculums'][0]
    assert curriculum_data['purchased'] is True
    assert curriculum_data['progress'] == 0  # pas de leçons complétées

@pytest.mark.django_db
def test_dashboard_with_completed_lessons(client):
    """
    Test dashboard progress calculation based on completed lessons.
    """
    user = User.objects.create_user(email='test@test.com', password='ComplexPassword123!')
    theme = Theme.objects.create(name='Test Thème')
    curriculum = Curriculum.objects.create(title='Test titre cursus', theme=theme, price=50)
    lesson1 = Lesson.objects.create(title='Test titre leçon 1', curriculum=curriculum, order=1, price=0)
    lesson2 = Lesson.objects.create(title='Test titre leçon 2', curriculum=curriculum, order=2, price=0)

    Payment.objects.create(user=user, curriculum=curriculum, amount=curriculum.price, status='paid')

    # User completes the first lesson
    LessonCompletion.objects.create(user=user, lesson=lesson1, is_completed=True)

    client.login(email='test@test.com', password='ComplexPassword123!')
    url = reverse('dashboard')
    response = client.get(url)

    assert response.status_code == 200

    curriculum_data = response.context['theme_with_curriculums'][0]['curriculums'][0]
    # Progressshould be 50% as 1 out of 2 lessons are completed
    assert curriculum_data['progress'] == 50

@pytest.mark.django_db
def test_dashboard_with_standalone_lessons(client):
    """
    Test dashboard view when standalone lessons (not entire curriculum) are purchased.
    """
    user = User.objects.create_user(email='test@test.com', password='ComplexPassword123!')
    theme = Theme.objects.create(name='Test Thème')
    curriculum = Curriculum.objects.create(title='Test titre cursus', theme=theme, price=50)
    lesson1 = Lesson.objects.create(title='Test titre leçon 1', curriculum=curriculum, order=1, price=0)
    lesson2 = Lesson.objects.create(title='Test titre leçon 2', curriculum=curriculum, order=2, price=0)

    # Payment for a standalone lesson (outside the full curriculum)
    Payment.objects.create(user=user, lesson=lesson1, amount=curriculum.price, status='paid')

    client.login(email='test@test.com', password='ComplexPassword123!')
    url = reverse('dashboard')
    response = client.get(url)

    assert response.status_code == 200

    standalone = response.context['standalone_lessons_by_theme']
    assert theme in standalone

    curriculum_lessons = standalone[theme][curriculum]
    # Lesson 1 should be marked as purchased
    lesson_data = next(ld for ld in curriculum_lessons if ld['lesson'] == lesson1)
    assert lesson_data['purchased'] is True

    # Lesson 2 should not be marked as purchased
    lesson_data2 = next(ld for ld in curriculum_lessons if ld['lesson'] == lesson2)
    assert lesson_data2['purchased'] is False
