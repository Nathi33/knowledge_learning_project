from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import Payment
from courses.models import Lesson

@login_required
def buy_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    Payment.objects.create(
        user=request.user,
        lesson=lesson,amount=lesson.price,
        status='paid' # à modifier/supprimer quand on aura intégré stripe
    )
    return redirect('lesson_detail', lesson_id=lesson.id)


