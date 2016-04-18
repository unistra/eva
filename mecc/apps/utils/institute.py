from mecc.apps.adm.models import MeccUser, Profile

from django.db.models import Q
from django.contrib.auth.models import User

def manage_dircomp_rac(new_username, profile, institute, request, name):
    """
    Create user if doesn't exist and give required profile anyway.
    Delete old user if had no more profile/permission
    """
    inst = {'rac': institute.id_rac, 'dircomp': institute.id_dircomp}

    if name == inst[profile]:
        return

    user_profile = Profile.objects.get(code=profile.upper())
    u = MeccUser.objects.filter(
        Q(cmp__contains=institute.code) &
        Q(profile__code__contains=profile.upper())
    )

    old = list(u[:1])
    if old:
        old[0].profile.remove(user_profile)
        profiles = old[0].profile.all()
        if len(profiles) < 1:
            old[0].user.delete()
            old[0].delete()

    if new_username in ['', ' ', None]:
        return

    user, user_created = User.objects.get_or_create(username=new_username)
    if user_created:
        user.first_name = request.POST.get(str(profile) + '_first_name', '')
        user.last_name = request.POST.get(str(profile) + '_last_name', '')
        user.email = request.POST.get(str(profile) + '_mail', '')
        user.save()

    meccuser, meccuser_created = MeccUser.objects.get_or_create(user=user)
    meccuser.profile.add(user_profile)
    meccuser.cmp = institute.code

    meccuser.save()
