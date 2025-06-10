from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Theme
from .models import Certificate
import logging

logger = logging.getLogger(__name__)

@login_required
def view_certificate(request, theme_id):
    """
    Displays a user's certificate for a given theme if eligible.

    If the user has not completed all lessons in the theme's curriculums,
    a page indicating they are not eligible for the certificate is shown.

    Parameters:
        request (HttpRequest): The incoming HTTP request.
        theme_id (int): The ID of the theme for which to display the certificate.

    Returns:
        HttpResponse: The certificate page or the "not eligible" page.
    """
    theme = get_object_or_404(Theme, id=theme_id)
    logger.info(f"Utilisateur {request.user.id} a accédé à la page de certificat pour le thème '{theme.name}' (ID {theme.id})")

    certificate, created = Certificate.objects.get_or_create(
        user=request.user, 
        theme=theme
    )
    if created:
        logger.info(f"Certificat créé pour l'utilisateur {request.user.id} - Thème : '{theme.name}' (ID {theme.id})")
    else:
        logger.debug(f"Certificat déjà existant pour l'utilisateur {request.user.id} - Thème : '{theme.name}' (ID {theme.id})")

    return render(request, 'certificates/certificate.html', {
        'certificate': certificate,
        'user': request.user,
    })


