from django.contrib.auth import login
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.encoding import force_bytes
from .tokens import activation_token_generator
from django.urls import reverse
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.conf import settings
from urllib.parse import quote_plus
from urllib.parse import urlencode

User = get_user_model()

def register_view(request):
    """
    Handle user registration.

    Displays a registration form, creates an inactive user upon successful submission,
    sends an activation email, and redirects to the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A rendered registration form or a redirect to login.
    """
    next_url = request.GET.get('next')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Do not activate the account immediately
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Creating the activation link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = activation_token_generator.make_token(user)

            params = {
                'uid': uid,
                'token': token,
            }
            if next_url:
                params['next'] = next_url

            activation_link = request.build_absolute_uri(
                reverse('confirm_activation') + '?' + urlencode(params)
            )

            # Sending the HTML activation email
            subject = 'Activation de votre compte E-learning'
            html_message = f'''
                <p>Bonjour {user.first_name} {user.last_name},</p>
                <p>Merci de vous être inscrit sur notre plateforme E-learning.</p>
                <p>Avant de pouvoir vous connecter, vous devez activer votre compte.</p>
                <p>Afin de vérifier votre adresse e-mail, veuillez cliquer sur le lien suivant :</p>
                <p><a href="{activation_link}" rel="noreferrer noopener" target="_blank" style="display:inline-block;padding:10px 20px;background-color:#82b864;color:white;text-decoration:none;border-radius:5px;">Activer mon compte</a></p>
                <p>Si le bouton ne fonctionne pas, copiez-collez le lien suivant dans votre navigateur :</p>
                <pre style="word-break: break-all; font-family: monospace;">{activation_link}</pre>
                <p>Merci et à bientôt sur notre plateforme !</p>
                <p>L'équipe Knowledge E-learning</p>
            '''
            # Convert HTML to plain text
            plain_message = strip_tags(html_message)  

            try:    
                send_mail(
                    subject,
                    plain_message,
                    'knowledge.elearning.plateform@gmail.com',
                    [user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print("Erreur lors de l'envoi du mail :", e)
                messages.error(request, "Une erreur s'est produite lors de l'envoi de l'email d'activation.")
                return redirect('login')
            
            # Redirect to confirmation page
            messages.success(request, 'Inscription réussie ! Un email d\'activation vous a été envoyé à votre adresse e-mail. Veuillez vérifier votre boîte de réception.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})

def confirm_activation(request):
    """
    Render a confirmation page after user registration.

    Displays a message indicating that an activation email has been sent.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A rendered confirmation page.
    """
    uidb64 = request.GET.get('uid') 
    token = request.GET.get('token')
    next_url = request.GET.get('next') or 'home'  

    if not uidb64 or not token:
        messages.error(request, "Lien d'activation invalide.")
        return redirect('login')
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and activation_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
            login(request, user, backend='users.backends.EmailBackend')
            messages.success(request, f"Bienvenue {user.first_name} {user.last_name}, votre compte a été activé avec succès !")
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'home')
        else:
            messages.success(request, f"Bienvenue {user.first_name} {user.last_name}, votre compte a été activé avec succès !")
            login(request, user, backend='users.backends.EmailBackend')
            return redirect(next_url if next_url else 'home')

    else:
        messages.error(request, "Le lien d'activation est invalide ou a expiré.")
        return redirect('login')

    

def activate(request, uidb64, token):
    """
    Activate a user account via an email verification link.

    Decodes the UID, verifies the token, activates the user, logs them in,
    and redirects to the homepage or a next URL if provided.

    Args:
        request (HttpRequest): The HTTP request object.
        uidb64 (str): Base64-encoded user ID.
        token (str): Verification token.

    Returns:
        HttpResponse: A redirect or an invalid activation message page.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        User = get_user_model()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and activation_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        user.backend = 'users.backends.EmailBackend'
        login(request, user)

        messages.success(request, f"Bienvenue {user.first_name} {user.last_name}, votre compte a été activé !")
        next_url = request.GET.get('next')
        return redirect(next_url if next_url else 'home')
    else:
        return render(request, 'users/activation_invalid.html')


class CustomLoginView(LoginView):
    """
    Custom login view.

    Uses a custom authentication form and displays a welcome message upon successful login.
    """
    template_name = 'users/login.html'  
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        """
        Display a success message and proceed with login if the form is valid.

        Args:
            form (AuthenticationForm): The validated authentication form.

        Returns:
            HttpResponseRedirect: A redirect to the success URL.
        """
        user = form.get_user()
        messages.success(self.request, f"Bienvenue {user.first_name} {user.last_name} !")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """
    Custom logout view.

    Displays a confirmation message after user logout.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Handle the logout request.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The response after logout.
        """
        messages.success(request, "Vous avez été déconnecté(e) avec succès.")
        return super().dispatch(request, *args, **kwargs)
    