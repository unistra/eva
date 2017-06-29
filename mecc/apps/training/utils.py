"""
Usefull stuff for trainings view
"""
from datetime import datetime

from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group

from mecc.apps.utils.queries import currentyear
from mecc.apps.training.models import Training
from mecc.apps.mecctable.models import StructureObject, ObjectsLink
from mecc.apps.utils.queries import currentyear


def training_has_consumed(training, current_year):
    """
    Return true if training has on of its object consumed by another training
    """
    all_links = ObjectsLink.objects.filter(code_year=current_year)
    all_id_imported = {link.id_child for link in all_links.filter(
        is_imported=True).exclude(id_training=training.id)}
    id_in_training = {link.id_child for link in all_links.filter(
        id_training=training.id).exclude(is_imported=True)}

    one_is_present = any(id_training in all_id_imported for id_training in id_in_training)

    message = _("Cela entraine la suppression du tableau MECC (les éléments \
    importés continuent d'exister dans leur formation d'orgine")

    return True if one_is_present else False


def remove_training(request, training_id):
    """
    Return dict telling if can be removed and ifnot why
    """
    current_year = currentyear().code_year

    def user_has_profile(user, profile, code_cmp):
        """
        Return true if user has this profile on cmp
        """
        profile_list = profile if isinstance(profile, list) else [profile]
        profiles = user.meccuser.profile.filter(
            cmp=code_cmp, code__in=profile_list)

        return True if profiles else False

    training = Training.objects.get(id=training_id)
    training_code = training.supply_cmp
    try:
        date_cmp = datetime.strftime(training.date_val_cmp, '%d/%m/%Y')
    except TypeError:
        date_cmp = None
    try:
        date_cfvu = datetime.strftime(training.date_val_cfvu, '%d/%m/%Y')
    except TypeError:
        date_cfvu = None
    structs = StructureObject.objects.filter(
        code_year=current_year, owner_training_id=training_id)

    mecc_validated = _("MECC validées en")
    removable = False
    message = _("Vous ne pouvez pas supprimer cette formation")
    # check training strucutre object are not used anywhere else
    if training_has_consumed(training, current_year):
        message = _("Le tableau MECC de cette formation contient des objets consomés par \
        d'autres formations. Veuillez contacter les responsables concernés via les outils \
        de gestion intégrés.")
        return {"removable": removable, "message": message}

    # check user can edit/remove it
    if user_has_profile(request.user, [
            'DIRETU', 'GESCOL', 'DIRCOMP', 'RAC', 'REFSCOL'
    ], training_code) or request.user.is_superuser:
        if training.date_val_cfvu:
            if user_has_profile(request.user, [
                    'DIRETU', 'GESCOL', 'DIRCOMP', 'RAC', 'REFSCOL'], training_code):
                message = _("%s CFVU le %s. La suppression n'est pas autorisée. \
                Veuillez contacter la DES si besoin" % (
                    mecc_validated, date_cfvu))
            if Group.objects.get(name='DES1') in request.user.groups.all(
            ) or request.user.is_superuser:
                removable = True
                message = _("%s CFVU le %s. \
                %s composante le %s.\
                Êtes vous sûr de vouloir supprimer ?" % (
                    mecc_validated, date_cfvu, mecc_validated, date_cmp))
            return {"removable": removable, "message": message}
        elif training.date_val_cmp:
            if user_has_profile(request.user, ['DIRETU', 'GESCOL'], training_code):
                message = _("%s composante le %s. \
                Vous n'êtes pas autorisé(e) à supprimer cette formation.\
                Veuillez contacter votre RAC ou référent outil si besoin." % (
                    mecc_validated, date_cmp))
            if Group.objects.get(name="DES1") in request.user.groups.all(
            ) or request.user.is_superuser\
                    or user_has_profile(request.user, ['DIRCOMP', 'RAC', 'REFSCOL'], training_code):
                removable = True
                message = _("%s composante le %s. Êtes vous sûr de vouloir supprimer ?" % (
                    mecc_validated, date_cmp))
            return {"removable": removable, "message": message}
        elif structs or training.has_custom_paragraph:
            removable = True
            message = _(
                "Il existe déjà des spécificités de règles \
                et/ou un tableau MECC pour cette formation.\
                Êtes vous sûr de vouloir supprimer ?")
        else:
            message = _("Êtes vous sûr de vouloir supprimer ?")
            removable = True
    return {"removable": removable, "message": message}
