from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import Payment
from courses.models import Lesson, Curriculum

@login_required
def buy_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    Payment.objects.create(
        user=request.user,
        lesson=lesson,
        amount=lesson.price,
        status='paid' # à modifier/supprimer quand on aura intégré stripe
    )
    return redirect('lesson_detail', lesson_id=lesson.id)


@login_required
def process_payment(request, curriculum_id):
    curriculum = get_object_or_404(Curriculum, id=curriculum_id)
    Payment.objects.create(
        user=request.user,
        curriculum=curriculum,
        amount=curriculum.price,
        status='paid' # à modifier/supprimer quand on aura intégré stripe
    )
    return redirect('curriculum_detail', curriculum_id=curriculum.id)

