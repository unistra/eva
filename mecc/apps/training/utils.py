"""
Usefull stuff for trainings view
"""
from datetime import datetime

from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group

from mecc.apps.utils.queries import currentyear
from mecc.apps.training.models import Training
from mecc.apps.mecctable.models import StructureObject, ObjectsLink


ALLS = ObjectsLink.objects.all()


def training_has_consumed(training, current_year):
    """
    Return true if training has on of its object consumed by another training
    """
    all_links = ALLS.filter(code_year=current_year)
    all_id_imported = {link.id_child for link in all_links.filter(
        is_imported=True).exclude(id_training=training.id)}
    id_in_training = {link.id_child for link in all_links.filter(
        id_training=training.id).exclude(is_imported=True)}

    one_is_present = any(
        id_training in all_id_imported for id_training in id_in_training)

    message = _("Cela entraine la suppression du tableau MECC (les éléments \
    importés continuent d'exister dans leur formation d'orgine")

    return True if one_is_present else False


def remove_training(request, training_id):
    """
    Return dict telling if can be removed and if not why
    """
    current_year = currentyear().code_year
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

    diret_gescol = ['DIRETU', 'GESCOL']
    others = ['DIRCOMP', 'RAC', 'REFSCOL']
    mecc_validated = _("MECC validées en")
    message = ""
    removable = True

    def has_consumed(removable, message):
        """" check training strucutre object are not used anywhere else """
        if training_has_consumed(training, current_year):
            removable = False
            message += _("Le tableau MECC contient des objets consommés par \
            d'autres formations. </br>Veuillez contacter les responsables des \
            formations concernés via les outils intégrés. </br> \
            <strong>Vous ne pouvez pas supprimer votre formation en l'état.</strong>")
        
        return removable, message

    def user_has_profile(user, profile, code_cmp):
        """
        Return true if user has this profile on cmp
        """
        profile_list = profile if isinstance(profile, list) else [profile]
        profiles = user.meccuser.profile.filter(
            cmp=code_cmp, code__in=profile_list)

        return True if profiles else False

    if user_has_profile(request.user, diret_gescol, training_code):
        if date_cfvu:
            removable = False
            message += ("%s CFVU le %s. La suppression n'est pas autorisée.<br> \
                Veuillez contacter la DES si besoin" % (
                mecc_validated, date_cfvu))
        if date_cmp:
            removable = False
            message += _("%s composante le %s. \
                Vous n'êtes pas autorisé(e) à supprimer cette formation.<br>\
                Veuillez contacter votre RAC ou référent outil si besoin." % (
                    mecc_validated, date_cmp))
        removable, message = has_consumed(removable, message)
        return {"removable": removable, "message": message}

    if user_has_profile(request.user, others, training_code):
        if date_cfvu:
            removable = False
            message += ("%s CFVU le %s. La suppression n'est pas autorisée. <br>\
                Veuillez contacter la DES si besoin" % (
                mecc_validated, date_cfvu))
        if date_cmp:
            message += _("%s composante le %s." % (mecc_validated, date_cmp))
            message += _("Êtes vous sûr de vouloir supprimer ?</br>")
        removable, message = has_consumed(removable, message)
        return {"removable": removable, "message": message}
        
    if Group.objects.get(name='DES1') in request.user.groups.all(
            ) or request.user.is_superuser:
        removable, message = has_consumed(removable, message)
        if date_cfvu and removable:
            message += _("%s CFVU le %s.</br>" % (mecc_validated, date_cfvu))
        if date_cmp and removable:
            message += _("%s composante le %s.</br>" % (mecc_validated, date_cmp))
        if removable:
            message += _("Êtes vous sûr de vouloir supprimer ?</br>")
        return {"removable": removable, "message": message}

    return {"removable": removable, "message": message}
