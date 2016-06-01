from mecc.apps.rules.models import Rule
from mecc.apps.years.models import UniversityYear


def rules_for_current_year(degree_type_code):
    """
    Return list of rules in use for current year applying to selected
    degree type
    """
    rules = Rule.objects.filter(degree_type__pk=degree_type_code).filter(
        code_year=UniversityYear.objects.get(
            is_target_year=True).code_year).filter(is_in_use=True)

    if len(rules) > 0:
        return rules
    else:
        return None


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
