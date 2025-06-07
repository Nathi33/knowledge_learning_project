from django import forms
from .models import Theme, Curriculum, Lesson
from django.forms import inlineformset_factory

class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = ['name']
        labels = {
            'name': 'Nom du thème',
        }


class CurriculumForm(forms.ModelForm):
    class Meta:
        model = Curriculum
        fields = ['title', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'curriculum-title-input'}),
        }
        labels = {
            'title': 'Titre du cursus',
            'price': 'Prix (€)',
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'order', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'lesson-title-input'}),
            'content': forms.Textarea(attrs={'class': 'lesson-content-textarea'}),
        }
        labels = {
            'title': 'Titre de la leçon',
            'content': 'Contenu de la leçon',
            'order': 'Ordre dans le cursus',
            'price': 'Prix (€)',
        }


CurriculumFormSet = inlineformset_factory(
    Theme, Curriculum,
    form=CurriculumForm,
    extra=0,
    can_delete=True
)

LessonFormSet = inlineformset_factory(
    Curriculum, 
    Lesson,
    form=LessonForm,
    extra=0,
    can_delete=True,
    min_num=0,
    validate_min=False
)