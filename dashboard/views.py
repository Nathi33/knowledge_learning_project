from django.contrib.auth.decorators import login_required
from payments.models import Payment
from courses.models import LessonCompletion, Curriculum, Lesson, Theme
from django.shortcuts import render
from collections import defaultdict


@login_required
def dashboard(request):
    user = request.user

    # Récupère les paiements valides de l'utilisateur
    payments = Payment.objects.filter(user=user, status='paid')

    # Cursus achetés
    purchased_curriculum_ids = payments.filter(curriculum__isnull=False).values_list('curriculum_id', flat=True)
    purchased_curriculums = Curriculum.objects.filter(id__in=purchased_curriculum_ids).prefetch_related('lessons', 'theme')

    # Leçons achetées individuellement
    purchased_lesson_ids = payments.filter(lesson__isnull=False).values_list('lesson_id', flat=True)
    purchased_lessons = Lesson.objects.filter(id__in=purchased_lesson_ids).select_related('curriculum', 'curriculum__theme')

    # Leçons complétées
    completed_lessons_ids = LessonCompletion.objects.filter(user=user, is_completed=True).values_list('lesson_id', flat=True)

    # Organisation des leçons achetées individuellement par thème et cursus
    standalone_lessons_by_theme = defaultdict(lambda: defaultdict(list))
    standalone_progress_by_theme = {}

    # Récupération de tous les thèmes concernés par des leçons achetées individuellement
    themes_with_standalone_lessons = Theme.objects.filter(curriculums__lessons__in=purchased_lessons).distinct()

    # Ajout de tous les cursus de ces thèmes pour prendre en compte toutes les leçons
    for theme in themes_with_standalone_lessons:
        for curriculum in Curriculum.objects.filter(theme=theme):
            for lesson_obj in curriculum.lessons.all():
                is_purchased = lesson_obj.id in purchased_lesson_ids
                is_completed = lesson_obj.id in completed_lessons_ids

                standalone_lessons_by_theme[theme][curriculum].append({
                    'lesson': lesson_obj,
                    'validated': is_completed,
                    'purchased': is_purchased
                })

    # Calcul de la progression totale pour les leçons achetées individuellement
    for theme, curriculums in standalone_lessons_by_theme.items():
        total = 0
        completed = 0
        for lessons in curriculums.values():
            for lesson_data in lessons:
                total += 1
                if lesson_data['validated']:
                    completed += 1
        progress = int((completed / total) * 100) if total else 0
        standalone_progress_by_theme[theme.id] = progress

    # On garde les thèmes ayant au moins un cursus acheté
    themes_with_purchased_curriculum = Theme.objects.filter(curriculums__in=purchased_curriculums).distinct()

    theme_with_curriculums = []
    theme_progress_by_theme = {}

    for theme in themes_with_purchased_curriculum:
        purchased = purchased_curriculums.filter(theme=theme)
        all_curriculums_in_theme = Curriculum.objects.filter(theme=theme)

        curriculums_data = []

        for curriculum in all_curriculums_in_theme:
            is_purchased = curriculum in purchased
            progress = 0

            if is_purchased:
                total = curriculum.lessons.count()
                completed = LessonCompletion.objects.filter(
                    user=user,
                    lesson__curriculum=curriculum,
                    is_completed=True
                ).count() 
                progress = int((completed / total) * 100) if total else 0

            curriculums_data.append({
                'curriculum': curriculum,
                'purchased': is_purchased,
                'progress': progress
            })

        # Calcul de la progression totale du thème
        total_lessons_in_theme = sum(c['curriculum'].lessons.count() for c in curriculums_data)
        completed_lessons_in_theme = LessonCompletion.objects.filter(
                user=user,
                lesson__curriculum__theme=theme,
                is_completed=True
            ).count()
        
        theme_progress = int((completed_lessons_in_theme / total_lessons_in_theme) * 100) if total_lessons_in_theme else 0

        theme_progress_by_theme[theme.id] = theme_progress

        theme_with_curriculums.append({
            'theme': theme,
            'curriculums': curriculums_data
            })
        
    # On convertit defaultdict en dict classique pour le template
    standalone_lessons_by_theme = {
        theme: dict(curriculums) 
        for theme, curriculums in standalone_lessons_by_theme.items()
    }

    return render(request, 'dashboard/dashboard.html', {
        'theme_with_curriculums': theme_with_curriculums,
        'standalone_lessons_by_theme': standalone_lessons_by_theme,
        'completed_lessons_ids': completed_lessons_ids,
        'theme_progress_by_theme': theme_progress_by_theme,
        'standalone_progress_by_theme': standalone_progress_by_theme,
    })





