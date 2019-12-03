"""
Usefull stuff for trainings view
"""
import logging
from datetime import datetime
from typing import List, Tuple

from britney.errors import SporeMethodStatusError
from django.contrib.auth.models import Group
from django.db.models import QuerySet, Q
from django.utils.translation import ugettext as _

from mecc.apps.institute.models import Institute
from mecc.apps.mecctable.models import StructureObject, ObjectsLink, Exam
from mecc.apps.training.models import Training
from mecc.apps.utils.queries import currentyear
from mecc.apps.utils.ws import get_user_from_ldap
from mecc.apps.years.models import UniversityYear


def link_is_excluded_by_rof(
        link: ObjectsLink,
        institutes_with_rof_support_ids: List[str]) -> bool:
    """
    Check if ObjectsLink is disabled in ROF (and therefore not considered in Eva)
    """
    # cf. di/mecc#147
    training = Training.objects.get(pk=link.id_training)
    if link.is_existing_rof is False and training.supply_cmp in institutes_with_rof_support_ids:
        return True
    if link.is_existing_rof is False and training.degree_type.ROF_code == 'EA':
        return True
    else:
        return False


def structure_object_is_excluded_by_rof(
        structure_object: StructureObject,
        training: Training,
        institutes_with_rof_support: List[str]) -> bool:
    """
    Check if structure_object is disabled in ROF (and therefore not considered in Eva)
    """
    # cf di/mecc#147
    if structure_object.is_existing_rof is False and training.supply_cmp in institutes_with_rof_support:
        return True
    if structure_object.is_existing_rof is False and training.degree_type.ROF_code == 'EA':
        return True
    else:
        return False


def get_links_for_structure(structure_object: StructureObject) -> QuerySet:
    """
    get queryset of ordered children links for structure_object
    """
    links = ObjectsLink.objects.filter(
        id_parent=structure_object.id,
    ).order_by('order_in_child')
    return links


def get_children_for_link(link: ObjectsLink,
                          training: Training,
                          ids_of_institutes_with_rof_support: List[str],
                          selected_links: List[ObjectsLink],
                          selected_structures: List[StructureObject]):
    """
    Get children (ObjectLinks and StructureObjects) for a link recursively
    excluding those disabled by ROF sync
    """
    if not link_is_excluded_by_rof(link, ids_of_institutes_with_rof_support):
        selected_links.append(link)
        structure = StructureObject.objects.get(pk=link.id_child)
        if not structure_object_is_excluded_by_rof(structure, training, ids_of_institutes_with_rof_support):
            if link.is_imported is False:
                selected_structures.append(structure)
                for link in get_links_for_structure(structure):
                    get_children_for_link(link, training, ids_of_institutes_with_rof_support, selected_links, selected_structures)
    return selected_links, selected_structures,


def build_objects_and_links_list(training: Training, ids_of_institutes_with_rof_support: List[str]):
    """
    Build a list of structure objects and links recursively, excluding those
    disabled by ROF sync and their descendants
    """
    current_year = currentyear().code_year
    current_structures = StructureObject.objects.filter(code_year=current_year)
    current_links = ObjectsLink.objects.filter(code_year=current_year)

    selected_links = []
    selected_structures = []

    # Si la composante en appui ROF ou la formation est de type Catalogue NS :
    # exclure si is_existing_rof = False
    if training.supply_cmp in ids_of_institutes_with_rof_support or training.degree_type.ROF_code == 'EA':
        current_links = current_links.exclude(
            is_existing_rof=False,
        )

    root_links = current_links.filter(
        id_parent='0',
        id_training=training.id
    ).order_by('order_in_child').distinct()

    for link in root_links:
        current_links, current_structures = get_children_for_link(link, training,
                                                                  ids_of_institutes_with_rof_support,
                                                                  selected_links, selected_structures)

    return current_links, current_structures


def consistency_check(training: Training):
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

    ids_of_institutes_with_rof_support = Institute.objects.filter(ROF_support=True).values_list('code', flat=True)
    links, training_structs = build_objects_and_links_list(training, ids_of_institutes_with_rof_support)

    links = ObjectsLink.objects.filter(
        id_training=training.id,
        id_child__in=[e.id for e in training_structs],
    )
    exams = Exam.objects.filter(id_attached__in=[e.id for e in training_structs])
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
        for struct in training_structs:
            proper_exam_1 = exams.filter(id_attached=struct.id, session=1)
            proper_exam_2 = exams.filter(id_attached=struct.id, session=2)
            try:
                link = links.get(id_child=struct.id)
            except ObjectsLink.DoesNotExist:
                # di/mecc#148 : links can ref another training in id_training, therefore use n_train_child
                link = ObjectsLink.objects.get(id_child=struct.id, n_train_child=training.id)
            if link_is_excluded_by_rof(link, ids_of_institutes_with_rof_support):
                continue

            # 0 Liste des UE qui ne respectent pas la règle coef = nb crédits / 3
            if "DU" not in training.degree_type.short_label:
                to_add = report['0']['objects']
                if struct.nature == 'UE':
                    if struct.ECTS_credit / 3 != link.coefficient:
                        to_add.append({
                            "0": struct.nature,
                            "1": struct.label,
                            "2": struct.ref_si_scol,
                            "3": "%s = %s" % (_("Crédits"), struct.ECTS_credit),
                            "4": "%s = <span class='red'>%s</span>" % (
                                 _("Coefficient"), link.coefficient)
                        })
            #  1 - 2
            if "E" in training.MECC_type and struct.nature == 'UE':
                # should those be filtered for is_existing_rof ??
                ue_children = struct.get_all_children
                children_exam_1 = exams.filter(
                    session=1,
                    id_attached__in=[child.id for child in ue_children]
                )
                # children_exam_2 = exams.filter(
                #     session=2,
                #     id_attached__in=[child.id for child in ue_children]
                # )

                # 1 Liste des UE en ECI ayant moins de 3 épreuves. en session 1
                if len(proper_exam_1) + len(children_exam_1) < 3:
                    to_add = report['1']['objects']
                    to_add.append({
                        "0": struct.nature,
                        "1": struct.label,
                        "2": struct.ref_si_scol,
                        "3": "%s = %s" % (
                            _("Nombre d'épreuves en session 1"),
                            "<span class='red'>%s</span>" % (len(proper_exam_1)+len(children_exam_1))),
                    })
                #
                # 2 Liste des UE en ECI ayant plus d'une épreuve en session 2 (Contrôle supprimé : di/mecc#145)
                # if len(proper_exam_2) + len(children_exam_2) > 1:
                #     to_add = report['2']['objects']
                #     to_add.append({
                #         "0": struc.nature,
                #         "1": struc.label,
                #         "2": struc.ref_si_scol,
                #         "3": "%s = %s" % (
                #             _("Nombre d'épreuves en session 2"),
                #             "<span class='red'>%s</span>" % (len(proper_exam_2)+len(children_exam_2))),
                #     })
            # 3 Liste des objets en CC/CT 2 sessions dont les épreuves et/ou les attributs d'épreuves diffèrent
            # en session 2
            if "C" in training.MECC_type and "2" in struct.session:
                to_add = report['3']['objects']
                can_be_added = {
                    "0": struct.nature,
                    "1": struct.label,
                    "2": struct.ref_si_scol,
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
                # 4 Liste des objets qui ont une note seuil
                if link.eliminatory_grade not in ['', ' ', None]:
                    to_add = report['4']['objects']
                    to_add.append({
                        "0": struct.nature,
                        "1": struct.label,
                        "2": struct.ref_si_scol,
                        "3": "%s = %s" % (
                            _("<span class='red'>Note seuil"),
                            "%s </span>" % link.eliminatory_grade)
                    })
                # 5 Liste des épreuves qui ont une note seuil
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
                            struct.nature, struct.label
                        ),
                        "2": struct.ref_si_scol,
                        "3": "%s = %s" % (
                            _("<span class='red'>Note seuil"),
                            "%s</span>" % e.eliminatory_grade)
                    })

            # 6 - 7 - 8
            if "master" in training.degree_type.short_label.lower():
                # 6 Liste des objets *non semestre* qui ont une note seuil
                if link.eliminatory_grade not in ['', ' ', None] and struct.nature != "SE":

                    to_add = report['6']['objects']
                    to_add.append({
                        "0": struct.nature,
                        "1": struct.label,
                        "2": struct.ref_si_scol,
                        "3": "%s = %s" % (
                            _("<span class='red'>Note seuil"),
                            "%s</span>" % link.eliminatory_grade)
                    })
                # 7 Liste des épreuves qui ont une note seuil
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
                            struct.nature, struct.label
                        ),
                        "2": struct.ref_si_scol,
                        "3": "%s = %s" % (
                            _("<span class='red'>Note seuil"),
                            "%s</span>" % e.eliminatory_grade)
                    })

                # 8 Liste des objets *semestre* qui n'ont pas de note seuil ou
                # dont la note seuil est différente de 10
                if struct.nature == "SE" and (link.eliminatory_grade in ['', ' ', None] or link.eliminatory_grade != 10):
                    to_add = report['8']['objects']
                    to_add.append({
                        "0": "%s : %s" % (struct.get_nature_display(), struct.label),
                        "1": struct.ref_si_scol,
                        "2": "<span class='red'>%s</span>" % _("Pas de note seuil") if link.eliminatory_grade in ['', ' ', None] else "<span class='red' %s = %s</span>" % (
                            _("Note seuil"), link.eliminatory_grade)
                    })
            # 9 Liste des objets *non semestre* dont le coefficient n'est pas compris entre 1 et 3
            if 'licence pro' in training.degree_type.short_label.lower() and struct.nature != 'SE':
                if not link.coefficient or not (0 < link.coefficient < 4):
                    to_add = report['9']['objects']
                    to_add.append({
                        "0": struct.nature,
                        "1": struct.label,
                        "2": struct.ref_si_scol,
                        "3": "<span class='red'>%s</span>" % _("Pas de coefficient") if not link.coefficient else "<span class='red'>%s = %s</span>" % (_("Coefficient"), link.coefficient)

                    })
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.exception(e)

    return report


def training_has_consumed(training, current_year):
    """
    Return true if training has on of its object consumed by another training
    """
    all_links = ObjectsLink.objects.filter(code_year=current_year)
    all_id_imported = {link.id_child for link in all_links.filter(
        is_imported=True).exclude(id_training=training.id)}
    id_in_training = {link.id_child for link in all_links.filter(
        id_training=training.id).exclude(is_imported=True)}

    one_is_present = any(
        id_training in all_id_imported for id_training in id_in_training)

    # message = _("Cela entraine la suppression du tableau MECC (les éléments \
    # importés continuent d'exister dans leur formation d'orgine")

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


def reapply_respforms(destination_training: Training, source_training: Training):
    # di/mecc#43 : copy respforms from previous year
    for respform in source_training.resp_formations.all():
        username = respform.user.username
        try:
            get_user_from_ldap(username)
            destination_training.resp_formations.add(respform)
        except SporeMethodStatusError as error:
            if error.response.status_code == 404:
                continue
            else:
                raise error


def reapply_attributes_previous_year(institute: Institute, current_year: UniversityYear):
    # di/mecc#43: reapply attributes from previous year
    skipped_trainings = []
    processed_trainings = []
    previous_year = get_previous_year(current_year)
    trainings_current_year = Training.objects.filter(
        supply_cmp=institute.code,
        code_year=current_year.code_year,
    )
    trainings_previous_year = Training.objects.filter(
        supply_cmp=institute.code,
        code_year=previous_year.code_year,
    )

    for training in trainings_current_year:
        if training.reappli_atb is True:
            # traitement déjà effectué ou modifications apportées
            skipped_trainings.append(training)
            continue
        if training.n_train == training.id or training.n_train is None:
            # La formation n'était pas présente l'année n-1
            skipped_trainings.append(training)
            continue
        else:
            try:
                # La formation était présente l'année n-1
                source_training = trainings_previous_year.get(pk=training.n_train)
            except Training.DoesNotExist:
                # training.n_train devrait référencer une formation existante
                message = "Training #{} has n_train attribute {} but training #{} does not exist".format(
                    training.id,
                    training.n_train,
                    training.n_train,
                )
                log_error(message)
                skipped_trainings.append(training)
                continue
        training.MECC_tab = source_training.MECC_tab
        reapply_respforms(training, source_training)
        processed_trainings.append(training)
        training.reappli_atb = True
        training.save()

    return processed_trainings, skipped_trainings


def get_previous_year(current_year: UniversityYear) -> UniversityYear:
    previous_year = UniversityYear.objects.exclude(
        code_year=current_year.code_year,
    ).order_by('code_year').last()  # type: UniversityYear
    return previous_year


def reapply_respens_and_attributes_from_previous_year(training: Training) -> Tuple[bool, str]:
    # cf di/mecc#44
    processed = True
    message = 'Traitement de récupération effectué.'
    if training.recup_atb_ens is True:
        return False, 'Le témoin recup_atb_ens vaut True'
    try:
        previous_training = Training.objects.get(pk=training.n_train)
    except Training.DoesNotExist:
        return False, 'Aucune formation correspondante dans l\'année précédente'
    if not previous_training.ref_cpa_rof:
        return False, 'La formation de l\'année précédente n\'a pas de réf. ROF'

    current_year = UniversityYear.objects.get(code_year=training.code_year)
    previous_year = get_previous_year(current_year)
    objects = StructureObject.objects.filter(
        owner_training_id=training.id,
        code_year=current_year.code_year,
    )
    for structure_object in objects:  # type: StructureObject
        try:
            previous_object = StructureObject.objects.get(
                pk=structure_object.auto_id,
                code_year=previous_year.code_year,
            )
        except StructureObject.DoesNotExist:
            continue
        try:
            get_user_from_ldap(structure_object.RESPENS_id)
            structure_object.RESPENS_id = previous_object.RESPENS_id
        except SporeMethodStatusError as error:
            if error.response.status_code == 404:
                structure_object.RESPENS_id = None
            else:
                raise error
        structure_object.external_name = previous_object.external_name
        structure_object.save()

    # do the "same" for ObjectLink
    links = ObjectsLink.objects.filter(
        ~Q(is_imported=True),   # exclude links with is_imported = True
        code_year=current_year.code_year,
        id_training=training.id,
    )
    for object_link in links:  # type: ObjectsLink
        try:
            if object_link.id_parent == 0:
                parent_auto_id = 0
            else:
                parent_object = StructureObject.objects.get(pk=object_link.id_parent)
                parent_auto_id = parent_object.auto_id
            child_object = StructureObject.objects.get(pk=object_link.id_child)
            previous_link = ObjectsLink.objects.get(
                id_parent=parent_auto_id,
                id_child=child_object.auto_id,
                code_year=previous_year.code_year,
            )
            object_link.coefficient = previous_link.coefficient
            object_link.eliminatory_grade = previous_link.eliminatory_grade
            object_link.save()
        except (ObjectsLink.DoesNotExist, StructureObject.DoesNotExist):
            continue

    training.recup_atb_ens = True
    training.save()

    return processed, message


def log_error(message: str) -> None:
    """
    Log error message to app log and Sentry
    """
    import logging
    from sentry_sdk import capture_message

    logger = logging.getLogger(__name__)
    logger.error(message)
    capture_message(message, level='error')
