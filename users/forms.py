from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']  # Champs à afficher dans le formulaire de connexion   

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  
        for fieldname in ['username']:
            self.fields[fieldname].help_text = ''  # Supprime le texte d'aide par défaut des champs  
   