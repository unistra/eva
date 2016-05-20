from django.db.models import Q
from mecc.apps.years.models import UniversityYear
from mecc.apps.rules.models import Rule

def rules_for_current_year(degree_type_code):
    rules = Rule.objects.filter(is_in_use=True).filter(degree_type__pk=degree_type_code)
    if len(rules) > 0 :
        return rules
    else:
        return None

def rules_since_ever(degree_type_code):
    rules = Rule.objects.filter(degree_type__pk=degree_type_code)
    if len(rules) > 0 :
        return rules
    else:
        return None
