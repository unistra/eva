from django import template
from django.contrib.auth.models import Group
from mecc.apps.adm.models import Profile


register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter(name='is_profile')
def is_profile(meccuser, profile_code):
    profile = Profile.objects.get(code=profile_code)
    return True if profile in meccuser.profile.all() else False


@register.filter(name='gas_profile')
def has_profile(meccuser, profiles):
    for e in profiles:
        profile = Profile.objects.get(code=e)
        if profile in meccuser.profile.all():
            return True
    return False

# @register.filter(name='in_list_profile')
# def in_list_profile(meccuser, list_profile):
#     profiles = meccuser.profile.all()
#     for e in list_profile:
#         profile = Profile.objects.get(code=e)
#         if profile in profiles:
#             return True
#     return False
