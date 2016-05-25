from functools import wraps
# from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden


def is_ajax_request(view_func):
    """
    Check if the request is ajax
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.is_ajax():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("<h1>Forbidden</h1>You do not have \
            permission to access this page.")
    return wrapper


def is_DES1(view_func):
    """
    Check if user belong to DES1 group
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.has_perm('unpaids.can_view_unpaid'):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("<h1>Forbidden</h1>You do not have \
            permission to access this page.")
    return wrapper
