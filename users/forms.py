from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new user with required fields: email, last name, and first name.

    Fields:
        email (EmailField): Required email address.
        last_name (CharField): Required last name.
        first_name (CharField): Required first name.
    """
    email = forms.EmailField(required=True, label="Adresse e-mail : ")  
    last_name = forms.CharField(max_length=30, required=True, label="Nom : ")
    first_name = forms.CharField(max_length=30, required=True, label="Prénom : ") 

    class Meta:
        model = CustomUser
        # Fields displayed in the user creation form
        fields = ['last_name', 'first_name', 'email', 'password1', 'password2']   
    
    def save(self, commit=True):
        """
        Save the new user instance with the provided email, last name, and first name.

        Args:
            commit (bool): Whether to save the user to the database immediately.

        Returns:
            user (CustomUser): The saved user instance.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.last_name = self.cleaned_data['last_name']
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
        return user
    
User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    """
    Authentication form that uses email instead of username to login.

    Fields:
        username (EmailField): Email field replacing the default username field.
    """
    username = forms.EmailField(label="Adresse e-mail : ", widget=forms.EmailInput(attrs={'autofocus': True}))
   
    def confirm_login_allowed(self, user):
        """
        Check if the given user account is active before allowing login.

        Raises:
            ValidationError: If the user account is inactive.
        """
        if not user.is_active:
            raise forms.ValidationError(
                "Ce compte n'est pas actif. Veuillez vérifier votre adresse e-mail pour l'activer.",
                code='inactive',
            )