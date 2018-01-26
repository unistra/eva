from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from mecc.apps.rules.models import Rule
from mecc.apps.years.models import UniversityYear
from mecc.apps.mecctable.models import StructureObject


def rules_since_ever(degree_type_code):
    """
    Return list of rules applyint to selected degree type
    """
    rules = Rule.objects.filter(degree_type__pk=degree_type_code)
    if len(rules) > 0:
        return rules
    else:
        return None


def rules_for_year(selected_year):
    """
    Return list of rules for selected year
    """
    rules = Rule.objects.filter(code_year=selected_year)
    if len(rules) > 0:
        return rules
    else:
        return None


def rules_degree_for_year(degree_type_code, year):
    """
    Return list of rules in use for selected year applying to selected
    degree type
    """
    r = rules_for_year(year)
    if r is None:
        return None

    rules = r.filter(degree_type__pk=degree_type_code).filter(is_in_use=True)

    if len(rules) > 0:
        return rules
    else:
        return None


def currentyear():
    """
    Return current year
    """
    return UniversityYear.objects.filter(is_target_year=True).first()


def institute_staff(institute_code):
    """
    Return list of staff people from an Institute
    """
    return User.objects.select_related().filter(meccuser__profile__cmp=institute_code)


def get_mecc_table_order(
        link, struc_respens, current_structures,
        current_links, current_exams, all_exam=False):
    """
    Recurse until end of time
    """
    links = not isinstance(link, (list, tuple)) and [link] or link
    stuff = []

    def get_childs(link, is_imported, user_can_edit=False, rank=0):
        """
        Looking for children in order to recurse on them
        """
        rank += 1
        not_yet_imported = False
        try:
            structure = current_structures.get(id=link.id_child)
            user_can_edit = True if structure.id in struc_respens else user_can_edit
        except ObjectDoesNotExist:
            not_yet_imported = True
            structure = StructureObject.objects.get(id=link.id_child)
        children = current_links.filter(
            id_parent=link.id_child).order_by('order_in_child')
        imported = True if link.is_imported or is_imported else False
        # ADDING FUN WITH EXAMS
        # Get 3 first exams_1 & exam_2
        exams_1 = current_exams.filter(
            id_attached=structure.id, session="1")
        exams_2 = current_exams.filter(
            id_attached=structure.id, session="2")
        items = {
            "link": link,
            'structure': structure,
            'is_imported': imported,
            'has_childs': True if len(children) > 0 else False,
            'children': [get_childs(
                e, imported, user_can_edit=user_can_edit, rank=rank) for e in children],
            'rank': rank - 1,
            'loop': range(0, rank - 1),
            'not_yet_imported': not_yet_imported,
            'exams_1': exams_1 if all_exam else exams_1[:3],
            'exams_1_count': True if exams_1.count() > 3 else False,
            'exams_2': exams_2 if all_exam else exams_2[:3],
            'exams_2_count': True if exams_2.count() > 3 else False,
            'can_be_edited': True if user_can_edit else False,
        }
        return items
    for link in links:
        imported = True if link.is_imported else False
        stuff.append(get_childs(link, imported))

    return stuff


def update_regime_session(training, regime, session):
    """
    update regime and session of training structure according to new elements
    """
    structs = StructureObject.objects.filter(owner_training_id=training.id)
    for struc in structs:
        struc.regime = regime
        struc.session = session
        struc.save()


def save_training_update_structs(training, regime_type, session_type):
    """
    Reapply regime and session to selected training and all it objects
    => return true if updated  and else if nothin' was done
    """
    # set regime and session type to new stuff
    old_session_type = training.session_type
    old_regime_type = training.MECC_type
    save_me = False

    if old_regime_type != regime_type:
        training.MECC_type = regime_type
        save_me = True
    if old_session_type != session_type:
        training.session_type = session_type
        save_me = True

    if save_me:
        training.save()

    return save_me