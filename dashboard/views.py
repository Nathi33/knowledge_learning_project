from django.contrib.auth.decorators import login_required
from payments.models import Payment
from courses.models import LessonCompletion, Curriculum, Lesson
from django.shortcuts import render
from collections import defaultdict


@login_required
def dashboard(request):
    user = request.user
    # Récupère les paiements "paid" de l'utilisateur
    payments = Payment.objects.filter(user=user, status='paid')

    # Récupère les cursus et leçons achetés par l'utilisateur
    purchased_curriculum_ids = payments.filter(curriculum__isnull=False).values_list('curriculum', flat=True)
    purchased_lesson_ids = payments.filter(lesson__isnull=False).values_list('lesson', flat=True)

    # Récupère les leçons et cursus associés
    purchased_curriculums = Curriculum.objects.filter(id__in=purchased_curriculum_ids)
    purchased_lessons = Lesson.objects.filter(id__in=purchased_lesson_ids)

    # Pour chaque cursus, vérification de la validation complète
    validated_curriculums = []
    for curriculum in purchased_curriculums:
        total_lessons = curriculum.lessons.count()
        completed_lessons_count = LessonCompletion.objects.filter(
            user=user, 
            lesson__curriculum=curriculum, 
            is_completed=True
        ).count()
        is_curriculum_validated = completed_lessons_count == total_lessons

        lessons_status = []
        for lesson in curriculum.lessons.all():
            is_completed = LessonCompletion.objects.filter(
                user=user, 
                lesson=lesson, 
                is_completed=True
            ).exists()
            lessons_status.append({
                'lesson': lesson,
                'validated': is_completed,
            })

        validated_curriculums.append({
            'curriculum': curriculum,
            'validated': is_curriculum_validated,
            'lessons': lessons_status
        })

    standalone_lessons_by_curriculum = defaultdict(list)

    for lesson in purchased_lessons:
        if lesson.curriculum:
            curriculum = lesson.curriculum
            is_completed = LessonCompletion.objects.filter(
                user=user, 
                lesson=lesson, 
                is_completed=True
            ).exists()

            if curriculum not in standalone_lessons_by_curriculum:
                for curr_lesson in curriculum.lessons.all():
                    # Vérifie si la leçon fait partie des leçons achetées
                    is_purchased = curr_lesson in purchased_lessons
                    is_completed = LessonCompletion.objects.filter(
                        user=user, 
                        lesson=curr_lesson, 
                        is_completed=True
                    ).exists() if is_purchased else False

                    standalone_lessons_by_curriculum[curriculum].append({
                        'lesson': curr_lesson,
                        'validated': is_completed,
                        'purchased': is_purchased,
                })
    
    context = {
        'validated_curriculums': validated_curriculums,
        'standalone_lessons_by_curriculum': dict(standalone_lessons_by_curriculum),
    }

    return render(request, 'dashboard/dashboard.html', context)
