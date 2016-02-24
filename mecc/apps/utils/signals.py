from django.db.models.signals import pre_save, post_delete, pre_delete
from django.dispatch import receiver
from mecc.apps.commission.models import ECICommissionMember
from django.contrib.auth.models import User
from mecc.apps.adm.models import MeccUser
from mecc.apps.institute.models import Institute

@receiver(pre_save, sender=ECICommissionMember)
def ECI_pre_save(sender, **kwargs):
    new_user = kwargs['instance']
    user = User.objects.create_user(new_user.username, email=new_user.email)
    user.last_name = new_user.last_name
    user.first_name = new_user.first_name
    user.save()
    meccuser = MeccUser.objects.create(user=user)
    meccuser.profile = 'ECI'
    meccuser.save()


@receiver(post_delete, sender=ECICommissionMember)
def ECI_post_delete(sender, **kwargs):
    to_del = kwargs['instance'].username
    user = User.objects.get(username=to_del)
    user.delete()


@receiver(pre_delete, sender=User)
def User_delete(sender, **kwargs):
    print(kwargs['instance'])


@receiver(pre_save, sender=Institute)
def Institute_pre_save(sender, **kwargs):
    for e in kwargs:
        print(e)
    print(kwargs['instance'])
    print(kwargs['using'])
