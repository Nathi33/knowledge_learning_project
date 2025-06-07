from django.shortcuts import render
from courses.models import Theme

def home(request):
    """
    Render the homepage displaying all available themes.

    Retrieves all Theme objects from the database and passes them
    to the 'core/home.html' template for rendering.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: The rendered homepage with the list of themes.
    """
    themes = Theme.objects.all()
    return render(request, 'core/home.html', {'themes': themes})

def under_construction(request):
    """
    Renders a simple 'Under Construction' page.
    
    This view is used to display a message indicating that the site is currently under construction.
    """
    return render(request, 'core/under_construction.html')





