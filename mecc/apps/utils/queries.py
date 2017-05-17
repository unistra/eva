from django.contrib.auth.models import User

from mecc.apps.rules.models import Rule
from mecc.apps.years.models import UniversityYear


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
    return UniversityYear.objects.filter(is_target_year=True).first()


def institute_staff(institute_code):
    """
    Return list of staff people from an Institute
    """
    return User.objects.select_related().filter(meccuser__profile__cmp=institute_code)
