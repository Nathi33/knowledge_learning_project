from django.contrib.auth.decorators import login_required
from payments.models import Payment
from courses.models import LessonCompletion, Curriculum, Lesson, Theme
from django.shortcuts import render
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    """
    Render the user's dashboard displaying their purchased curriculums and lessons,
    along with their completion progress organized by themes and curriculums.

    This view performs the following steps:
    - Retrieves all successful payments for the logged-in user.
    - Identifies purchased curriculums and individually purchased lessons.
    - Fetches lessons completed by the user.
    - Organizes individually purchased lessons by theme and curriculum,
      including whether each lesson is purchased and/or completed.
    - Calculates progress percentages for themes based on completed lessons.
    - Lists curriculums purchased by the user within each theme, 
      computing progress per curriculum and overall theme progress.
    - Passes structured data to the 'dashboard/dashboard.html' template for rendering.

    Context passed to the template:
    - 'theme_with_curriculums': List of themes with their curriculums,
      each curriculum annotated with purchase status and progress percentage.
    - 'standalone_lessons_by_theme': Dict mapping themes to their curriculums
      and lessons bought individually, with purchase and completion flags.
    - 'completed_lessons_ids': IDs of lessons marked as completed by the user.
    - 'theme_progress_by_theme': Progress percentage of completed lessons per theme for purchased curriculums.
    - 'standalone_progress_by_theme': Progress percentage of completed individually purchased lessons per theme.

    Requires user authentication.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered dashboard page with user’s learning progress and purchases.
    """
    user = request.user
    logger.info(f"L'utilisateur {user.last_name} {user.first_name} a accédé à son tableau de bord.")

    # Retrieves valid payments from the user
    payments = Payment.objects.filter(user=user, status='paid')
    logger.debug(f"Nombre de paiements valides trouvés pour l'utilisateur {user.last_name} {user.first_name}: {payments.count()}")

    # Curriculums purchased
    purchased_curriculum_ids = payments.filter(curriculum__isnull=False).values_list('curriculum_id', flat=True)
    purchased_curriculums = Curriculum.objects.filter(id__in=purchased_curriculum_ids).prefetch_related('lessons', 'theme')
    logger.debug(f"Nombre de curriculums achetés trouvés pour l'utilisateur {user.last_name} {user.first_name}: {purchased_curriculum_ids.count()}")

    # Lessons purchased individually
    purchased_lesson_ids = payments.filter(lesson__isnull=False).values_list('lesson_id', flat=True)
    purchased_lessons = Lesson.objects.filter(id__in=purchased_lesson_ids).select_related('curriculum', 'curriculum__theme')
    logger.debug(f"Nombre de leçons achetées individuellement trouvées pour l'utilisateur {user.last_name} {user.first_name}: {purchased_lesson_ids.count()}")

    # Lessons completed
    completed_lessons_ids = LessonCompletion.objects.filter(user=user, is_completed=True).values_list('lesson_id', flat=True)
    logger.debug(f"Nombre de leçons terminées trouvées pour l'utilisateur {user.last_name} {user.first_name}: {completed_lessons_ids.count()}")

    # Organization of lessons purchased individually by theme and curriculum
    standalone_lessons_by_theme = defaultdict(lambda: defaultdict(list))
    standalone_progress_by_theme = {}

    # Recovery of all themes covered by lessons purchased individually
    themes_with_standalone_lessons = Theme.objects.filter(curriculums__lessons__in=purchased_lessons).distinct()
    logger.debug(f"Nombre de thèmes avec des leçons achetées individuellement: {themes_with_standalone_lessons.count()}")

    # Added all the curriculums for these themes to cover all lessons
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

    # Calculating total progress for lessons purchased individually
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
    logger.debug(f"Progression des leçons achetées individuellement par thème: {standalone_progress_by_theme}")

    # We keep the themes with at least one course purchased
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

        # Calculating the total progress of the theme
        total_lessons_in_theme = sum(c['curriculum'].lessons.count() for c in curriculums_data)
        completed_lessons_in_theme = LessonCompletion.objects.filter(
                user=user,
                lesson__curriculum__theme=theme,
                is_completed=True
            ).count()
        
        theme_progress = int((completed_lessons_in_theme / total_lessons_in_theme) * 100) if total_lessons_in_theme else 0

        theme_progress_by_theme[theme.id] = theme_progress

        logger.debug(f"Progression du thème {theme.name} pour l'utilisateur {user.last_name} {user.first_name}: {theme_progress}%")

        theme_with_curriculums.append({
            'theme': theme,
            'curriculums': curriculums_data
            })
        
    # We convert defaultdict to classic dict for the template
    standalone_lessons_by_theme = {
        theme: dict(curriculums) 
        for theme, curriculums in standalone_lessons_by_theme.items()
    }

    logger.info(f"Tableau de bord rendu pour l'utilisateur {user.last_name} {user.first_name} avec {len(theme_with_curriculums)} thèmes et {len(standalone_lessons_by_theme)} leçons individuelles.")

    return render(request, 'dashboard/dashboard.html', {
        'theme_with_curriculums': theme_with_curriculums,
        'standalone_lessons_by_theme': standalone_lessons_by_theme,
        'completed_lessons_ids': completed_lessons_ids,
        'theme_progress_by_theme': theme_progress_by_theme,
        'standalone_progress_by_theme': standalone_progress_by_theme,
    })





