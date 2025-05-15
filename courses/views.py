from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Curriculum, Lesson, LessonCompletion, Theme


def themes_list(request):
    themes = Theme.objects.all()
    return render(request, 'courses/themes_list.html', {'themes': themes})


def theme_detail(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)
    curriculums = theme.curriculums.all()
    return render(request, 'courses/theme_detail.html', {
        'theme': theme,
        'curriculums': curriculums,
    })


def curriculum_detail(request, curriculum_id):
    curriculum = get_object_or_404(Curriculum, id=curriculum_id)
    lessons = curriculum.lessons.order_by('order')
    return render(request, 'courses/curriculum_detail.html', {
        'curriculum': curriculum,
        'lessons': lessons
    })


@login_required
def purchase_curriculum(request, curriculum_id):
    curriculum = get_object_or_404(Curriculum, id=curriculum_id)
    return render(request, 'courses/purchase_curriculum.html', {'curriculum': curriculum})


@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    # Accès refusé si l'utilisateur n'a pas payé la leçon ni le cursus
    if not (lesson.is_paid_by_user(request.user) or lesson.curriculum.is_paid_by_user(request.user)):
        return render(request, 'courses/access_denied.html', {'lesson': lesson})
    is_completed = LessonCompletion.objects.filter(
        user=request.user, lesson=lesson, is_completed=True
    ).exists()
    return render(request, 'courses/lesson_detail.html', {
        'lesson': lesson,
        'is_completed': is_completed,
    })


@login_required
def complete_lesson(request, lesson_id):
    if request.method == "POST":
        lesson = get_object_or_404(Lesson, id=lesson_id)
        completion, created = LessonCompletion.objects.get_or_create(
            user = request.user,
            lesson=lesson,
            defaults={'is_completed': True}
        )
        if not created and not completion.is_completed:
            completion.is_completed = True
            completion.save()
    return redirect('lesson_detail', lesson_id=lesson.id)