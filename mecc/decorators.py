from functools import wraps
# from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from mecc.apps.training.models import Training
from mecc.apps.utils.querries import currentyear
from django.db.models import Q
from mecc.apps.adm.models import Profile


def is_correct_respform(view_func):
    """
    Check if the request is ajax
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        print('*************')
        training = Training.objects.get(id=kwargs.get('id'))
        user_profiles = request.user.meccuser.profile.all()
        can_do_alot = Profile.objects.filter(cmp=training.supply_cmp).filter(
            year=currentyear().code_year).filter(
            Q(code='DIRCOMP') | Q(code='RAC'))
        dircomp_or_rac = any(True for x in can_do_alot if x in user_profiles)

        b = [e.id for e in training.resp_formations.all()]
        if request.user.meccuser.id in b or request.user.is_superuser or dircomp_or_rac:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("<h1>Forbidden</h1>You do not have \
            permission to access this page.")
    return wrapper


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


def user_can_spoof(view_func):
    """
    Check if user can spoof identity
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.has_perm('adm.can_spoof_user') or \
                'DES3' in request.user.groups.values_list('name', flat=True):
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
        group = Group.objects.get(name='DES1')
        if group in request.user.groups.all() or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("<h1>Forbidden</h1>You do not have \
            permission to access this page.")
    return wrapper


def has_requested_cmp(view_func):
    @wraps(view_func)
    def wrapper(self, *args, **kwargs):
        try:
            if self.kwargs.get('cmp') == self.request.user.meccuser.cmp:
                return view_func(self, *args, **kwargs)
        except ObjectDoesNotExist:
            # Nothin to do here since user such as superuser can not having
            # meccuser informations
            pass

        if self.request.user.is_superuser or \
           'DES1' in self.request.user.groups.all():
            return view_func(self, *args, **kwargs)
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
