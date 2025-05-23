from django.contrib.auth import login
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.conf import settings

def register_view(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Ne pas activer le compte immédiatement
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Création du lien d'activation
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = request.build_absolute_uri(
                reverse('activate', kwargs={'uidb64': uid, 'token': token})
            )
            if next_url:
                activation_link += f'?next={next_url}'

            # Envoi de l'email d'activation HTML
            subject = 'Activation de votre compte E-learning'
            html_message = f'''
                <p>Bonjour {user.first_name} {user.last_name},</p>
                <p>Merci de vous être inscrit sur notre plateforme E-learning.</p>
                <p>Avant de pouvoir vous connecter, vous devez activer votre compte.</p>
                <p>Afin de vérifier votre adresse e-mail, veuillez cliquer sur le lien suivant :</p>
                <p><a href="{activation_link}" style="display:inline-block;padding:10px 20px;background-color:#82b864;color:white;text-decoration:none;border-radius:5px;">Activer mon compte</a></p>
                <p>Merci et à bientôt sur notre plateforme !</p>
                <p>L'équipe Knowledge E-learning</p>
            '''
            plain_message = strip_tags(html_message)  # Convertir le message HTML en texte brut
            
            print('EMAIL_HOST:', settings.EMAIL_HOST)
            print('EMAIL_PORT:', settings.EMAIL_PORT)
            print('EMAIL_HOST_USER:', settings.EMAIL_HOST_USER)
            print('EMAIL_USE_TLS:', settings.EMAIL_USE_TLS)
                
            send_mail(
                subject,
                plain_message,
                'knowledge.elearning.plateform@gmail.com',
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Redirection vers la page de confirmation
            return render(request, 'users/confirmation_sent.html', {'email': user.email})
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})

def activate(request, uidb64, token):
    next_url = request.GET.get('next')
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        User = get_user_model()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        user.backend = 'users.backends.EmailBackend'
        login(request, user)  # Connecter l'utilisateur après activation
        messages.success(request, 'Votre compte a été activé avec succès et vous êtes maintenant connecté !')

        if next_url:
            return redirect(next_url)
        return redirect('home')  # Rediriger vers la page d'accueil ou une autre page
    else:
        return render(request, 'users/activation_invalid.html')


class CustomLoginView(LoginView):
    template_name = 'users/login.html'  
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f"Bienvenue {user.first_name} {user.last_name} !")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Vous avez été déconnecté(e) avec succès.")
        return super().dispatch(request, *args, **kwargs)
    