from django.shortcuts import render
from courses.models import Theme

def home(request):
    themes = Theme.objects.all()
    return render(request, 'home.html', {'themes': themes})


