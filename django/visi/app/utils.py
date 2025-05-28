from django.http import HttpResponse
from functools import wraps
from django.shortcuts import redirect


def role_required(allowed_roles):
    """
    Custom decorator to restrict access to users with specific roles.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponse(
                    "You must be logged in to access this page.", status=403
                )
            if request.user.role not in allowed_roles:
                return HttpResponse(
                    "You do not have permission to access this page.", status=403
                )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# made this to not allow users to create events, availabilities, etc. if they dont have a profile
def profile_required(view_func):
    @wraps(view_func)
    def checkprofile(request, *args, **kwargs):
        user = request.user
        if not (
            hasattr(user, "fan_user")
            or hasattr(user, "artist_user")
            or hasattr(user, "venue_user")
            or hasattr(user, "doorman_user")
        ):
            return redirect("createprofile")
        return view_func(request, *args, **kwargs)

    return checkprofile
