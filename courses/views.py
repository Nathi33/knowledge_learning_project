from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import Curriculum, Lesson, LessonCompletion, Theme
from .forms import ThemeForm, CurriculumFormSet, LessonFormSet
from django.contrib import messages
from django.core.management import call_command
from django.http import JsonResponse

def staff_required(view_func):
    """
    Decorator to check if the user is a staff member.
    """
    return user_passes_test(lambda u: u.is_staff)(view_func)

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

@staff_required
def edit_theme(request, theme_id):
    """
    Edit an existing theme. Only accessible to staff members.

    Args:
        request (HttpRequest): The HTTP request object.
        theme_id (int): Primary key of the theme to edit.

    Returns:
        HttpResponse: Rendered template with the form for editing the theme.
    """
    theme = get_object_or_404(Theme, pk=theme_id)

    if request.method == 'POST':

        theme_form = ThemeForm(request.POST, instance=theme)
        curriculum_formset = CurriculumFormSet(request.POST, instance=theme, prefix='curriculum')

        lesson_formsets = []
        all_valid = theme_form.is_valid() and curriculum_formset.is_valid()

        for i, curriculum_form in enumerate(curriculum_formset.forms):
                curriculum_instance = curriculum_form.instance
                prefix = f'lesson-{i}'
                lesson_formset = LessonFormSet(request.POST, instance=curriculum_instance, prefix=prefix)
                lesson_formsets.append(lesson_formset)
                all_valid = all_valid and lesson_formset.is_valid()

        if all_valid:
            theme_instance = theme_form.save()

            curriculum_instances = curriculum_formset.save(commit=False)
            for curriculum in curriculum_instances:
                curriculum.theme = theme_instance
                curriculum.save()
            
            for obj in curriculum_formset.deleted_objects:
                obj.delete()

            for i, curriculum in enumerate(curriculum_instances):
                lesson_formsets[i].instance = curriculum
                
            for lesson_formset in lesson_formsets:
                    lesson_formset.save()
            
            messages.success(request, 'Mise à jour réalisée avec succès.')
            return redirect('themes_list')
        else:
            messages.error(request, 'Erreur dans le formulaire. Veuillez corriger les erreurs.')

    else:
        theme_form = ThemeForm(instance=theme)
        curriculum_formset = CurriculumFormSet(instance=theme, prefix='curriculum')

        lesson_formsets = []
        for i, curriculum_form in enumerate(curriculum_formset.forms):
            if curriculum_form.instance.pk:
                prefix = f'lesson-{i}'
                formset = LessonFormSet(instance=curriculum_form.instance, prefix=prefix)
                lesson_formsets.append((curriculum_form, formset))
            else:
                lesson_formsets.append((curriculum_form, None))

    empty_curriculum_form = CurriculumFormSet(prefix='curriculum').empty_form
    empty_lesson_formset = LessonFormSet(prefix='lesson-__prefix__')
    empty_lesson_formset.empty_form.prefix = 'lesson-__prefix__'

    return render(request, 'courses/edit_theme.html', {
        'form': theme_form,
        'formset': curriculum_formset,
        'lesson_formsets': lesson_formsets,
        'theme': theme,
        'empty_curriculum_form': empty_curriculum_form,
        'empty_lesson_formset': empty_lesson_formset,
    })

@staff_required
def delete_theme(request, theme_id):
    """
    Delete a theme. Only accessible to staff members.

    Args:
        request (HttpRequest): The HTTP request object.
        theme_id (int): Primary key of the theme to delete.

    Returns:
        HttpResponseRedirect: Redirects to the themes list after deletion.
    """
    theme = get_object_or_404(Theme, pk=theme_id)
    if request.method == 'POST':
        theme.delete()
        messages.success(request, 'Thème supprimé avec succès.')
        return redirect('themes_list')
    return render(request, 'courses/delete_theme.html', {'theme': theme})

@staff_required
def create_theme(request):
    if request.method == 'POST':
        form = ThemeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le nouveau thème a été créé avec succès.')
            return redirect('themes_list')
        else:
            messages.error(request, 'Erreur dans le formulaire. Veuillez corriger les erreurs.')
    else:
        form = ThemeForm()
    return render(request, 'courses/create_theme.html', {'form': form})

def import_data(request):
    try:
        call_command('loaddata', 'courses/fixtures/data.json')
        return JsonResponse({'status': 'success', 'message': 'Données importées'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})