from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm 


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Connection automatique après inscription
            return redirect('home') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'users/login.html'  # Chemin vers le template de connexion
    # redirect_authenticated_user = True  # Redirige les utilisateurs déjà connectés vers la page d'accueil

    # def get_success_url(self):
    #     return self.get_redirect_url() or '/'  # Redirige vers la page d'accueil après connexion réussie