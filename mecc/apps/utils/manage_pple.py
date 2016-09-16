from mecc.apps.adm.models import MeccUser, Profile
from mecc.apps.training.models import Training
from django.db.models import Q
from django.contrib.auth.models import User
from mecc.apps.utils.querries import currentyear


def manage_dircomp_rac(new_username, profile, institute, request, name):
    """
    Create user if doesn't exist and give required profile anyway.
    Delete old user if had no more profile/permission
    """
    inst = {'rac': institute.id_rac, 'dircomp': institute.id_dircomp}
    display = {'rac': ' Responsable administratif',
               'dircomp': 'Directeur de composante'}
    if name == inst[profile]:
        return

    user_profile, created = Profile.objects.get_or_create(
        code=profile.upper(),
        label=display.get(profile),
        cmp=institute.code,
        year=currentyear().code_year
    )

    u = MeccUser.objects.filter(
        Q(cmp__contains=institute.code) &
        Q(profile__code__contains=profile.upper())
    )
    old = list(u[:1])
    if old:
        profile_to_del = old[0].profile.filter(code=profile.upper(), cmp=institute.code).first()
        old[0].profile.remove(profile_to_del)
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


def manage_respform(dic, t_id):
    """
    Create / delete repsform for a training
    """
    supply_cmp = Training.objects.get(id=t_id).supply_cmp
    user_profile = Profile.objects.filter(Q(code="RESPFORM", cmp=supply_cmp))
    training = Training.objects.get(id=dic.get('formation'))
    user, user_created = User.objects.get_or_create(
        username=dic.get('username'))
    if user_created:
        user.username = dic.get('username')
        user.first_name = dic.get('firstname')
        user.last_name = dic.get('name')
        user.email = dic.get('mail')
        user.save()

    meccuser, meccuser_created = MeccUser.objects.get_or_create(user=user)
    u_p = user_profile.first()

    if 'add_respform' in dic:
        if len(user_profile) < 1:
            u_p = Profile.objects.create(
                code="RESPFORM", cmp=supply_cmp,
                label="Responsable de formation", year=currentyear().code_year)
        meccuser.cmp = dic.get('cmp')
        meccuser.profile.add(u_p)
        training.resp_formations.add(meccuser)
        training.save()
        meccuser.save()
        return True

    if 'remove' in dic:
        train_respform = Training.objects.all().filter(
            resp_formations__user__username=dic.get('username')
        )
        training.resp_formations.remove(meccuser)
        if len(train_respform) < 1:
            meccuser.profile.remove(u_p)
        if len(meccuser.profile.all()) < 1 and len(user.groups.all()) < 1:
            meccuser.user.delete()
            meccuser.delete()
        return True

    return False
