import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Theme, Curriculum, Lesson, LessonCompletion
from payments.models import Payment

User = get_user_model()

@pytest.mark.django_db
def test_dashboard_requires_login(client):
    url = reverse('dashboard')
    response = client.get(url)
    # Vérifie que la redirection vers login a lieu
    assert response.status_code == 302
    assert '/login/' in response.url

@pytest.mark.django_db
def test_dashboard_empty_data(client):
    user = User.objects.create_user(email='user@test.com', password='password')
    client.login(email='user@test.com', password='password')

    url = reverse('dashboard')
    response = client.get(url)

    assert response.status_code == 200
    # Pas de cursus, pas de leçons
    assert b'No curriculum' not in response.content  # adapter selon ton template
    # Ici on peut tester que les contextes sont vides ou bien initialisés
    assert response.context['theme_with_curriculums'] == []
    assert response.context['standalone_lessons_by_theme'] == {}

@pytest.mark.django_db
def test_dashboard_with_purchased_curriculum(client):
    user = User.objects.create_user(email='user@test.com', password='password')
    theme = Theme.objects.create(name='Theme 1')
    curriculum = Curriculum.objects.create(title='Curriculum 1', theme=theme, price=10)
    lesson1 = Lesson.objects.create(title='Lesson 1', curriculum=curriculum, order=1, price=0)
    lesson2 = Lesson.objects.create(title='Lesson 2', curriculum=curriculum, order=2, price=0)

    # Création d'un paiement lié au curriculum
    Payment.objects.create(user=user, curriculum=curriculum, amount=curriculum.price, status='paid')

    client.login(email='user@test.com', password='password')
    url = reverse('dashboard')
    response = client.get(url)

    assert response.status_code == 200

    # Le thème doit être présent dans le contexte
    themes = [item['theme'] for item in response.context['theme_with_curriculums']]
    assert theme in themes

    # Le curriculum doit être marqué comme acheté
    curriculum_data = response.context['theme_with_curriculums'][0]['curriculums'][0]
    assert curriculum_data['purchased'] is True
    assert curriculum_data['progress'] == 0  # pas de leçons complétées

@pytest.mark.django_db
def test_dashboard_with_completed_lessons(client):
    user = User.objects.create_user(email='user@test.com', password='password')
    theme = Theme.objects.create(name='Theme 1')
    curriculum = Curriculum.objects.create(title='Curriculum 1', theme=theme, price=10)
    lesson1 = Lesson.objects.create(title='Lesson 1', curriculum=curriculum, order=1, price=0)
    lesson2 = Lesson.objects.create(title='Lesson 2', curriculum=curriculum, order=2, price=0)

    Payment.objects.create(user=user, curriculum=curriculum, amount=curriculum.price, status='paid')

    # L'utilisateur a complété la première leçon
    LessonCompletion.objects.create(user=user, lesson=lesson1, is_completed=True)

    client.login(email='user@test.com', password='password')
    url = reverse('dashboard')
    response = client.get(url)

    assert response.status_code == 200

    curriculum_data = response.context['theme_with_curriculums'][0]['curriculums'][0]
    # Progression devrait être 50% car 1/2 leçons complétées
    assert curriculum_data['progress'] == 50

@pytest.mark.django_db
def test_dashboard_with_standalone_lessons(client):
    user = User.objects.create_user(email='user@test.com', password='password')
    theme = Theme.objects.create(name='Theme 1')
    curriculum = Curriculum.objects.create(title='Curriculum 1', theme=theme, price=10)
    lesson1 = Lesson.objects.create(title='Lesson 1', curriculum=curriculum, order=1, price=0)
    lesson2 = Lesson.objects.create(title='Lesson 2', curriculum=curriculum, order=2, price=0)

    # Paiement d'une leçon individuelle (hors cursus)
    Payment.objects.create(user=user, lesson=lesson1, amount=curriculum.price, status='paid')

    client.login(email='user@test.com', password='password')
    url = reverse('dashboard')
    response = client.get(url)

    assert response.status_code == 200

    standalone = response.context['standalone_lessons_by_theme']
    assert theme in standalone

    curriculum_lessons = standalone[theme][curriculum]
    # On doit retrouver la leçon1 marquée comme achetée
    lesson_data = next(ld for ld in curriculum_lessons if ld['lesson'] == lesson1)
    assert lesson_data['purchased'] is True

    # La leçon2 n'est pas achetée
    lesson_data2 = next(ld for ld in curriculum_lessons if ld['lesson'] == lesson2)
    assert lesson_data2['purchased'] is False
