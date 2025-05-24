import threading

_user = threading.local()

class CurrentUserMiddleware:
    """
    Middleware that stores the current user in a thread-local variable.

    This allows access to the current user from anywhere in the code
    (e.g., models, signals, utils) without explicitly passing the request object.

    Attributes:
        get_response (callable): The next middleware or view to call.
    """
    def __init__(self, get_response):
        """
        Initializes the middleware with the given get_response function.

        Args:
            get_response (callable): The next layer to call in the middleware stack.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Processes the incoming request, storing the current user in thread-local storage.

        Args:
            request (HttpRequest): The current HTTP request.

        Returns:
            HttpResponse: The response returned by the next middleware/view.
        """
        _user.value = request.user
        response = self.get_response(request)
        return response

def get_current_user():
    """
    Retrieves the current user from thread-local storage.

    Returns:
        User or None: The currently authenticated user, or None if not set.
    """
    return getattr(_user, 'value', None)
