"""
Usefull stuff for trainings view
"""
import logging
from datetime import datetime

from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group

from mecc.apps.institute.models import Institute
from mecc.apps.utils.queries import currentyear
from mecc.apps.training.models import Training
from mecc.apps.mecctable.models import StructureObject, ObjectsLink, Exam

LOGGER = logging.getLogger(__name__)

ALLS = ObjectsLink.objects.all()


def consistency_check(training):
    """
    Lets do some checking:
    Pour tous les types de diplôme sauf les diplômes d’université
    (crédits= 0), et quel que soit le régime
        =>  Liste des UE qui ne respectent pas la règle
            Coefficient = nombre de crédits/3

    Pour les formations en ECI
        =>  Liste des UE en ECI ayant moins de 3 épreuves en
            session 1 (indiquer le nombre d’épreuves)
        =>  Liste des UE en ECI ayant plus d’une épreuve en
            session 2 (indiquer le nombre d’épreuves)

    Pour les formations en CC/CT
        =>  Liste des objets en CC/CT 2 sessions, dont les épreuves
            et/ou les attributs d’épreuves diffèrent en session 2

    Pour les Licences
        =>  Liste des objets qui ont une note seuil
        =>  Liste des épreuves qui ont une note seuil

    Pour les Masters
        =>  Liste des objets non semestre qui ont une note seuil
        =>  Liste des épreuves qui ont une note seuils
        =>  Liste des objets semestre qui n’ont pas de note seuil
            ou dont la note seuil est différente de 10

    Pour les Licences professionnelles
        =>  Liste des objets non semestre dont le coefficient n’est
            pas compris entre 1 et 3
    """
    structs = StructureObject.objects.filter(owner_training_id=training.id)
    links = ObjectsLink.objects.filter(
        id_training=training.id, id_child__in=[e.id for e in structs])
    exams = Exam.objects.filter(id_attached__in=[e.id for e in structs])
    try:
        report = {
            '0': {"title": _(
                "Liste des UE qui ne respectent pas la règle Coefficient \
= nombre de crédits/3"),
                "objects": []},
            '1': {"title": _(
                "Liste des UE en ECI ayant moins de 3 épreuves en session 1"),
                "objects": []},
            '2': {"title": _(
                "Liste des UE en ECI ayant plus d’une épreuve en session 2"),
                "objects": []},
            '3': {"title": _(
                "Liste des objets en CC/CT 2 sessions, dont les épreuves \
et/ou les attributs d’épreuves diffèrent en session 2"),
                "objects": []},
            '4': {"title": _(
                "Liste des objets qui ont une note seuil"),
                "objects": []},
            '5': {"title": _(
                "Liste des épreuves qui ont une note seuil"),
                "objects": []},
            '6': {"title": _(
                "Liste des objets non semestre qui ont une note seuil"),
                "objects": []},
            '7': {"title": _(
                "Liste des épreuves qui ont une note seuil"),
                "objects": []},
            '8': {"title": _(
                "Liste des objets semestre qui n’ont pas de note seuil \
ou dont la note seuil est différente de 10"),
                "objects": []},
            '9': {"title": _(
                "Liste des objets non semestre dont le coefficient n’est pas \
compris entre 1 et 3"),
                "objects": []}
        }
        for struc in structs:
            proper_exam_1 = exams.filter(id_attached=struc.id, session=1)
            proper_exam_2 = exams.filter(id_attached=struc.id, session=2)
            link = links.get(id_child=struc.id)
            # 0
            if "DU" not in training.degree_type.short_label:
                to_add = report['0']['objects']
                if struc.nature == 'UE':
                    if struc.ECTS_credit / 3 != link.coefficient:
                        to_add.append({
                            "0": struc.nature,
                            "1": struc.label,
                            "2": struc.ref_si_scol,
                            "3": "%s = %s" % (_("Crédits"), struc.ECTS_credit),
                            "4": "%s = <span class='red'>%s</span>" % (
                                 _("Coefficient"), link.coefficient)
                        })
            #  1 - 2 
            if "E" in training.MECC_type and struc.nature == 'UE':
                ue_children = struc.get_all_children
                children_exam_1 = exams.filter(
                    session=1,
                    id_attached__in=[child.id for child in ue_children]
                )
                children_exam_2 = exams.filter(
                    session=2,
                    id_attached__in=[child.id for child in ue_children]
                )
                # 1
                if len(proper_exam_1) + len(children_exam_1) < 3:
                    to_add = report['1']['objects']
                    to_add.append({
                        "0": struc.nature,
                        "1": struc.label,
                        "2": struc.ref_si_scol,
                        "3": "%s = %s" % (
                            _("Nombre d'épreuves en session 1"),
                            "<span class='red'>%s</span>" % (len(proper_exam_1)+len(children_exam_1))),
                    })
                # 2
                if len(proper_exam_2) + len(children_exam_2) > 1:
                    to_add = report['2']['objects']
                    to_add.append({
                        "0": struc.nature,
                        "1": struc.label,
                        "2": struc.ref_si_scol,
                        "3": "%s = %s" % (
                            _("Nombre d'épreuves en session 2"),
                            "<span class='red'>%s</span>" % (len(proper_exam_2)+len(children_exam_2))),
                    })
            # 3
            if "C" in training.MECC_type and "2" in struc.session:
                to_add = report['3']['objects']
                can_be_added = {
                    "0": struc.nature,
                    "1": struc.label,
                    "2": struc.ref_si_scol,
                    "3": _("<span class='red'>Les épreuves \
                    de la session 2 sont différentes</span>")
                }
                yet_done = False
                if len(proper_exam_1) != len(proper_exam_2):
                    to_add.append(can_be_added)
                    yet_done = True
                if not yet_done and proper_exam_1:
                    for e in proper_exam_1:
                        e2 = proper_exam_2.filter(_id=e._id).first()
                        if not yet_done and (e.type_exam != e2.type_exam or
                                             e.label != e2.label or
                                             e.exam_duration_h != e2.exam_duration_h or
                                             e.exam_duration_m != e2.exam_duration_m or
                                             e.coefficient != e2.coefficient or
                                             e.eliminatory_grade != e2.eliminatory_grade): # TODO
                            to_add.append(can_be_added)
                            yet_done = True
            # 4 -5
            if "licence" in training.degree_type.short_label.lower():
                # 4
                if link.eliminatory_grade not in ['', ' ', None]:
                    to_add = report['4']['objects']
                    to_add.append({
                        "0": struc.nature,
                        "1": struc.label,
                        "2": struc.ref_si_scol,
                        "3": "%s = %s" % (
                            _("<span class='red'>Note seuil"),
                            "%s </span>" % link.eliminatory_grade)
                    })
                # 5
                e1_with_elim = proper_exam_1.exclude(
                    eliminatory_grade=None)
                e2_with_elim = proper_exam_2.exclude(
                    eliminatory_grade=None)
                to_add = report['5']['objects']

                for e in e1_with_elim | e2_with_elim:  # merge queryset !
                    to_add.append({
                        "0": "%s : %s" % (_("Epreuve"), e.label),
                        "1": "%s : %s de l'objet : %s - %s" % (
                            _("Session"), e.session,
                            struc.nature, struc.label
                        ),
                        "2": struc.ref_si_scol,
                        "3": "%s = %s" % (
                            _("<span class='red'>Note seuil"),
                            "%s</span>" % e.eliminatory_grade)
                    })
            # 6 - 7 - 8
            if "master" in training.degree_type.short_label.lower():
                # 6
                if link.eliminatory_grade not in ['', ' ', None] and struc.nature != "SE":

                    to_add = report['6']['objects']
                    to_add.append({
                        "0": struc.nature,
                        "1": struc.label,
                        "2": struc.ref_si_scol,
                        "3": "%s = %s" % (
                            _("<span class='red'>Note seuil"),
                            "%s</span>" % link.eliminatory_grade)
                    })
                # 7
                e1_with_elim = proper_exam_1.exclude(
                    eliminatory_grade=None)
                e2_with_elim = proper_exam_2.exclude(
                    eliminatory_grade=None)
                to_add = report['7']['objects']

                for e in e1_with_elim | e2_with_elim:  # merge queryset !
                    to_add.append({
                        "0": "%s : %s" % (_("Epreuve"), e.label),
                        "1": "%s : %s de l'objet : %s - %s" % (
                            _("Session"), e.session,
                            struc.nature, struc.label
                        ),
                        "2": struc.ref_si_scol,
                        "3": "%s = %s" % (
                            _("<span class='red'>Note seuil"),
                            "%s</span>" % e.eliminatory_grade)
                    })

                # 8
                if struc.nature == "SE" and (link.eliminatory_grade in ['', ' ', None] or link.eliminatory_grade != 10):
                    to_add = report['8']['objects']
                    to_add.append({
                        "0": "%s : %s" % (struc.get_nature_display(), struc.label),
                        "1": struc.ref_si_scol,
                        "2": "<span class='red'>%s</span>" % _("Pas de note seuil") if link.eliminatory_grade in ['', ' ', None] else "<span class='red' %s = %s</span>" % (
                            _("Note seuil"), link.eliminatory_grade)
                    })
            # 9
            if 'licence pro' in training.degree_type.short_label.lower() and struc.nature != 'SE':
                if not link.coefficient or not (0 < link.coefficient < 4):
                    to_add = report['9']['objects']
                    to_add.append({
                        "0": struc.nature,
                        "1": struc.label,
                        "2": struc.ref_si_scol,
                        "3": "<span class='red'>%s</span>" % _("Pas de coefficient") if not link.coefficient else "<span class='red'>%s = %s</span>" % (_("Coefficient"), link.coefficient)

                    })
    except Exception as e:
        LOGGER.error('Consistency check error __: \n{error}'.format(error=e))
    return report


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
    confirmed = request.GET.get('confirm')
    institute = Institute.objects.get(code__exact=training.supply_cmp)

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
    others = ['DIRCOMP', 'RAC', 'REFAPP']
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
            <strong>Vous ne pouvez pas supprimer votre formation en l'état.</strong></br>")

        return removable, message

    def user_has_profile(user, profile, code_cmp):
        """
        Return true if user has this profile on cmp
        """
        profile_list = profile if isinstance(profile, list) else [profile]
        profiles = user.meccuser.profile.filter(
            cmp=code_cmp, code__in=profile_list)
        return True if profiles else False

    if institute.ROF_support:
        return {
            "removable": False,
            "message": _("Le support ROF est activé pour la composante. La formation ne peut pas être supprimée")
        }

    if user_has_profile(request.user, diret_gescol, training_code):
        if date_cfvu:
            removable = False
            message += ("%s CFVU le %s. La suppression n'est pas autorisée.<br> \
                Veuillez contacter la DES si besoin.</br>" % (
                mecc_validated, date_cfvu))
            return {"removable": removable, "message": message}

        if date_cmp:
            removable = False
            message += _("%s composante le %s.</br> \
                Vous n'êtes pas autorisé(e) à supprimer cette formation.<br>\
                Veuillez contacter votre RAC ou référent outil si besoin.</br>" % (
                mecc_validated, date_cmp))
        if removable:
            removable, message = has_consumed(removable, message)
        return {"removable": removable, "message": message}

    if user_has_profile(request.user, others, training_code):
        if date_cfvu:
            removable = False
            message += ("%s CFVU le %s. La suppression n'est pas autorisée. <br>\
                Veuillez contacter la DES si besoin.</br>" % (
                mecc_validated, date_cfvu))
            return {"removable": removable, "message": message}

        if date_cmp:
            removable = False
            if not confirmed:
                confirmed = "TODO"
                message += _("%s composante le %s.</br>" %
                             (mecc_validated, date_cmp))
                message += _("Êtes vous sûr de vouloir supprimer ?</br>")
                return {"removable": removable, "message": message,
                        'confirmed': confirmed}

        removable, message = has_consumed(removable, message)
        return {"removable": removable, "message": message}

    if Group.objects.get(name='DES1') in request.user.groups.all(
    ) or request.user.is_superuser:
        if date_cmp and not confirmed:
            removable = False
            confirmed = "TODO"
            message += _("%s composante le %s.</br>" %
                         (mecc_validated, date_cmp))
            if date_cfvu:
                message += _("%s CFVU le %s.</br>" %
                             (mecc_validated, date_cfvu))

            message += _("Êtes vous sûr de vouloir supprimer ?</br>")
            return {"removable": removable, "message": message,
                    'confirmed': confirmed}

        if removable:
            removable, message = has_consumed(removable, message)

        return {"removable": removable, "message": message, "confirmed": confirmed}
