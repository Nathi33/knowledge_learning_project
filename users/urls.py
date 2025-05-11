from django.urls import path
from .views import register_view, CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),  # URL pour la connexion
    path('register/', register_view, name='register'),  # URL pour l'inscription
    path('logout/', LogoutView.as_view(), name='logout'),  # URL pour la déconnexion 
]