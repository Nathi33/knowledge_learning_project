from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Theme
from .models import Certificate


@login_required
def view_certificate(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)

    # Vérification que l'utilisateur a bien terminé toutes les leçons
    curriculums = theme.curriculums.all()
    for curriculum in curriculums:
        for lesson in curriculum.lessons.all():
            if not lesson.is_completed_by_user(request.user):
                return render(request, 'certificates/not_eligible.html', {
                    'theme': theme
                })
            
    # Création du certificat
    certificate, created = Certificate.objects.get_or_create(
        user=request.user, 
        theme=theme
    )

    return render(request, 'certificates/certificate.html', {
        'certificate': certificate
    })


