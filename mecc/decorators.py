from functools import wraps
# from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.contrib.auth.models import Group
from django_cas.decorators import user_passes_test
from mecc.apps.training.models import Training
from mecc.apps.mecctable.models import StructureObject
from django.db.models import Q
from mecc.apps.adm.models import Profile


def can_edit_or_read(request, training, user):
    user_profiles = user.meccuser.profile.all()
    # Read and write rights
    can_do_alot = Profile.objects.filter(cmp=training.supply_cmp).filter(
        code__in=['DIRCOMP', 'RAC', 'REFAPP', 'GESCOL', 'DIRETU', 'RESPFORM'])

    allowed = any(True for x in can_do_alot if x in user_profiles)  \
        or 'DES1' in [e.name for e in user.groups.all()]
    resp_form = [e.id for e in training.resp_formations.all()]
    request.environ['allowed'] = allowed
    # Read only part
    institutes_not_supply = [
        e.code for e in training.institutes.all() if
        e.code not in training.supply_cmp]
    can_consult = Profile.objects.filter(
        cmp__in=institutes_not_supply,
        code__in=['DIRCOMP', 'RAC', 'REFAPP', 'GESCOL', 'DIRETU'])
    read_only = any(True for x in can_consult if x in user_profiles)
    request.environ['read_only'] = read_only
    # return view if allowed to at least read else rise 403
    if user.meccuser.id in resp_form or user.is_superuser or \
       allowed or read_only:
        return True
    # Structure object permission:
    s_o = StructureObject.objects.filter(
        owner_training_id=training.id, RESPENS_id=request.user.username)
    if s_o:
        request.environ['read_only'] = True
        return True
    return False


def is_correct_respform(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        t_id = kwargs.get('training_id')
        if t_id is None:
            t_id = kwargs.get('id')
        if t_id is None:
            raise Exception('Cannot retrive correct Formation')
        training = Training.objects.get(id=t_id)

        if can_edit_or_read(request, training, request.user):
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

        authorized = any(
            True for x in [
                e.cmp for e in self.request.user.meccuser.profile.all()
                if e.code in ['DIRETU', 'REFAPP', 'GESCOL', 'DIRCOMP', 'RAC']
            ] if x in self.request.path
        )

        if self.request.user.is_superuser or authorized or \
           'DES1' in [e.name for e in self.request.user.groups.all()]:
            return view_func(self, *args, **kwargs)

        return HttpResponseForbidden("<h1>Forbidden</h1>You do not have \
            permission to access this page.")
    return wrapper


def has_cmp(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        authorized = any(
            True for x in [
                e.cmp for e in request.user.meccuser.profile.all()
                if e.code in ['ECI', 'DIRETU', 'REFAPP', 'GESCOL', 'DIRCOMP', 'RAC']
            ] if x in request.path
        )

        if request.user.is_superuser or authorized or \
           'DES1' in [e.name for e in request.user.groups.all()]:
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


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
            return True
        return False
    return user_passes_test(in_groups)


def profile_required(*profile_names):
    """Requires user membership in at least one of the profiles passed in."""
    def in_profiles(u):
        if bool(u.meccuser.profile.filter(code__in=profile_names)) | u.is_superuser:
            return True
        return False
    return user_passes_test(in_profiles)


def profile_or_group_required(profile_names, group_names):
    """Requires user membership in profile or group"""
    def in_profile_or_group(u):
        if profile_required(profile_names) or group_required(group_names):
            return True
        return False
    return user_passes_test(in_profile_or_group)
