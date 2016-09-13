from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from mecc.apps.commission.models import ECICommissionMember
from mecc.apps.adm.models import Profile
from django.contrib.auth.models import User
from mecc.apps.adm.models import MeccUser, Profile
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError as ie
from mecc.apps.utils.querries import currentyear


@receiver(post_save, sender=User)
def User_post_save(sender, **kwargs):
    """
    Create MECCUser right after user is created
    """
    if kwargs.get('raw', False):  # Do not proceed if fixture
        return

    user = kwargs.get('instance')

    for e in User.objects.all():
        try:
            meccuser = MeccUser.objects.get(user=user)
        except ObjectDoesNotExist:
            meccuser = MeccUser.objects.create(user=user)


@receiver(pre_save, sender=ECICommissionMember)
def ECI_pre_save(sender, **kwargs):
    """
    Add corresponding profile to new ECI commission member
    """
    if kwargs.get('raw', False):  # Do not proceed if fixture
        return
    new_user = kwargs.get('instance')
    try:
        user = User.objects.create_user(
            new_user.username, email=new_user.email)
    except (IntegrityError, ie):
        user = User.objects.get(username=new_user.username)
    user.last_name = new_user.last_name
    user.first_name = new_user.first_name
    user.save()
    try:
        meccuser = MeccUser.objects.get(user__username=new_user.username)
    except ObjectDoesNotExist:
        meccuser = MeccUser.objects.create(user=user)
    eci = Profile.objects.get(code='ECI')
    meccuser.profile.add(eci)
    meccuser.save()


@receiver(post_delete, sender=ECICommissionMember)
def ECI_post_delete(sender, **kwargs):
    """
    Delete profile and if there isn't any other delete user
    """
    if kwargs.get('raw', False):  # Usefull for fixtures
        return
    to_del = kwargs['instance'].username
    meccuser = MeccUser.objects.get(user__username=to_del)
    eci = Profile.objects.get(code='ECI')
    meccuser.profile.remove(eci)
    profiles = meccuser.profile.all()
    if len(profiles) < 1 and not meccuser.user.is_superuser:
        meccuser.user.delete()
        meccuser.delete()
