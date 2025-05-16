from django.http import HttpResponse
from functools import wraps

def role_required(allowed_roles):
    """
    Custom decorator to restrict access to users with specific roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponse("You must be logged in to access this page.", status=403)
            if request.user.role not in allowed_roles:
                return HttpResponse("You do not have permission to access this page.", status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator