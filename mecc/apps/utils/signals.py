from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from mecc.apps.commission.models import ECICommissionMember
from django.contrib.auth.models import User
from mecc.apps.adm.models import MeccUser, Profile
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


@receiver(pre_save, sender=ECICommissionMember)
def ECI_pre_save(sender, **kwargs):
    """
    Add corresponding profile to new ECI commission member
    """
    if kwargs.get('raw', False):
        return
    new_user = kwargs['instance']
    try:
        user = User.objects.create_user(new_user.username, email=new_user.email)
    except IntegrityError:
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
    if kwargs.get('raw', False):
        return
    to_del = kwargs['instance'].username
    meccuser = MeccUser.objects.get(user__username=to_del)
    eci = Profile.objects.get(code='ECI')
    meccuser.profile.remove(eci)
    profiles = meccuser.profile.all()
    if len(profiles) < 1:
        meccuser.user.delete()
        meccuser.delete()
