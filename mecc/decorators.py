from functools import wraps
# from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.contrib.auth.models import Group


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
    def wrapper(request, group_name, *args, **kwargs):
        group = Group.objects.get(name=group_name)
        if group in request.user.groups.all():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("<h1>Forbidden</h1>You do not have \
            permission to access this page.")
    return wrapper


def is_post_request(view_func):
    """
    Check if the request is POST
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("<h1>Forbidden</h1>You do not have \
            permission to access this page.")
    return wrapper
