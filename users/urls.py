from django.urls import path
from .views import register_view, CustomLoginView, activate, CustomLogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),  # URL pour la connexion
    path('register/', register_view, name='register'),  # URL pour l'inscription
    path('logout/', CustomLogoutView.as_view(), name='logout'),  # URL pour la déconnexion 
    path('activate/<uidb64>/<token>/', activate, name='activate'),  # URL pour l'activation du compte
]