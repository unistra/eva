"""
Signals are used on variable elements such as :
    - DELETE on Training
    - SAVE on User
    - SAVE and DELETE on ECICommissionMember
"""
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.utils import IntegrityError as ie
from django.core.exceptions import ObjectDoesNotExist
from mecc.apps.commission.models import ECICommissionMember
from mecc.apps.utils.queries import currentyear
from mecc.apps.adm.models import MeccUser, Profile
from mecc.apps.training.models import Training, AdditionalParagraph, \
    SpecificParagraph
from mecc.apps.mecctable.models import ObjectsLink, StructureObject


@receiver(post_delete, sender=Training)
def Training_post_delete(sender, **kwargs):
    """
    When a Training is deleted, derogations and additional paragraphs are
    useless and so need to be deleted, the same for linksobjects and structureobject
    which are not used anymore
    """
    # 1. get concerned training
    training = kwargs.get('instance')
    # 2. get additionals and specifics concerned
    additionals = AdditionalParagraph.objects.filter(
        training=training)
    derogs = SpecificParagraph.objects.filter(
        training=training)
    # 3. remove them
    for additionnal in additionals:
        additionnal.delete()
    for derog in derogs:
        derog.delete()
    # 4. get objects link and structures objects
    links = ObjectsLink.objects.filter(id_training=training.id)
    structs = StructureObject.objects.filter(
        id__in=[link.id_child for link in links])
    # 5. get all objects link using concerned structs not in this training
    used = ObjectsLink.objects.filter(id_child__in=[struct.id for struct in structs]).exclude(
        id_training=training.id)
    # 6. delete struct if no training use it
    for struct in structs:
        if struct.id not in [link.id_child for link in used]:
            struct.delete()
    # 7. delete all link related to the training concerned
    for link in links:
        link.delete()
    # 8. dance :)


@receiver(post_save, sender=User)
def User_post_save(sender, **kwargs):
    """
    Create MECCUser right after user is created
    """
    if kwargs.get('raw', False):  # Do not proceed if fixture
        return

    user = kwargs.get('instance')

    # CAPITALIZE USERS' LASTNAME
    User.objects.filter(id=user.id).update(last_name=user.last_name.upper())

    for e in User.objects.all():
        try:
            MeccUser.objects.get(user=user)
        except ObjectDoesNotExist:
            MeccUser.objects.create(user=user)


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
    eci, create = Profile.objects.get_or_create(
        code='ECI', label="Membre de la Commission ECI",
        year=currentyear().code_year)
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
    profiles = meccuser.profile.all()
    eci = profiles.get(code='ECI')
    meccuser.profile.remove(eci)
    if len(profiles) < 1 and not meccuser.user.is_superuser:
        meccuser.user.delete()
        meccuser.delete()
