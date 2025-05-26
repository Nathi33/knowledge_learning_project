from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Curriculum, Lesson, LessonCompletion, Theme
from django.core.management import call_command
from django.http import JsonResponse

def themes_list(request):
    """
    Render a page listing all available course themes.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered template with the list of themes.
    """
    themes = Theme.objects.all()
    return render(request, 'courses/themes_list.html', {'themes': themes})

def theme_detail(request, theme_id):
    """
    Display detailed information about a specific theme including its curriculums.

    Args:
        request (HttpRequest): The HTTP request object.
        theme_id (int): Primary key of the theme to display.

    Returns:
        HttpResponse: Rendered template with the theme and its curriculums.
    """
    theme = get_object_or_404(Theme, id=theme_id)
    curriculums = theme.curriculums.all()
    return render(request, 'courses/theme_detail.html', {
        'theme': theme,
        'curriculums': curriculums,
    })

def curriculum_detail(request, curriculum_id):
    """
    Display detailed information about a curriculum and its lessons.

    Args:
        request (HttpRequest): The HTTP request object.
        curriculum_id (int): Primary key of the curriculum to display.

    Returns:
        HttpResponse: Rendered template with curriculum details and ordered lessons.
    """
    curriculum = get_object_or_404(Curriculum, id=curriculum_id)
    lessons = curriculum.lessons.order_by('order')
    return render(request, 'courses/curriculum_detail.html', {
        'curriculum': curriculum,
        'lessons': lessons
    })

@login_required
def purchase_curriculum(request, curriculum_id):
    """
    View to initiate purchase of a curriculum. Requires user to be logged in.

    Args:
        request (HttpRequest): The HTTP request object.
        curriculum_id (int): Primary key of the curriculum to purchase.

    Returns:
        HttpResponse: Rendered purchase page for the curriculum.
    """
    curriculum = get_object_or_404(Curriculum, id=curriculum_id)
    return render(request, 'courses/purchase_curriculum.html', {'curriculum': curriculum})

@login_required
def lesson_detail(request, lesson_id):
    """
    Display the lesson content if the user has purchased access.

    Args:
        request (HttpRequest): The HTTP request object.
        lesson_id (int): Primary key of the lesson to display.

    Returns:
        HttpResponse: Rendered lesson detail page or access denied page.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    # Access denied if the user has not paid for the lesson or the course
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
    """
    Mark a lesson as completed for the logged-in user.

    Args:
        request (HttpRequest): The HTTP request object.
        lesson_id (int): Primary key of the lesson to mark complete.

    Returns:
        HttpResponseRedirect: Redirect to dashboard after completion.
    """
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
    return redirect('dashboard')

def import_data(request):
    try:
        call_command('loaddata', 'fixtures/data.json')
        return JsonResponse({'status': 'success', 'message': 'Données importées'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})