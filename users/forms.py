from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse e-mail : ")  
    last_name = forms.CharField(max_length=30, required=True, label="Nom : ")
    first_name = forms.CharField(max_length=30, required=True, label="Prénom : ") 

    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'email', 'password1', 'password2']  # Champs à afficher dans le formulaire de connexion   

    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.last_name = self.cleaned_data['last_name']
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
        return user
    
User = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Adresse e-mail : ", widget=forms.EmailInput(attrs={'autofocus': True}))
   
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                "Ce compte n'est pas actif. Veuillez vérifier votre adresse e-mail pour l'activer.",
                code='inactive',
            )