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
    profile = Profile.objects.get(code=code)
    return True if profile in meccuser.profile.all() else False
