"""
View for document generator 3000
"""
from django.utils.translation import ugettext as _
from django.shortcuts import render,  redirect
from django.http import JsonResponse

from mecc.apps.institute.models import Institute
from mecc.apps.utils.queries import currentyear
from mecc.apps.years.models import UniversityYear, InstituteYear


def home(request, template='doc_generator/home.html'):
    """
    Home screen for generator 3000
    """
    data = {}
    all_institutes = Institute.objects.all()
    profiles = request.user.meccuser.profile.all()
    institute_year = InstituteYear.objects.filter(
        code_year=currentyear().code_year)
    if request.user.is_superuser or 'DES1' in [
            e.name for e in request.user.groups.all()]:
        data['institutes'] = [(e, institute_year.get(id_cmp=e.id))
                              for e in all_institutes]
    else:
        data['institutes'] = [(e, institute_year.get(
            id_cmp=e.id)) for e in all_institutes.filter(
            code__in=[e.cmp for e in profiles])]
    target = []
    profiles_code = [e.code for e in profiles]
    if any(True for profile in profiles if profile.code in [
            'RESPFORM', 'RESPENS']):
        target.append({
            'code': "review_my",
            'label': _("Relecture (mes formations)"),
            'order': 4,
        })
        if 'RESPENS' not in profiles_code:
            target.extend([{
                'code': "prepare_cc_my",
                'label': _("Préparation Conseil de composante (mes formations)"),
                'order': 6,
            }, {
                'code': "publish_my",
                'label': _("Publication (mes formations validées en CFVU)"),
                'order': 9,
            }])

    if any(True for profile in profiles if profile.code in [
            'DES1', 'DIRCOMP', 'RAC', 'REFAPP', 'DIRETU', 'GESCOL']):
        target.extend([{
            'code': "review_all",
            'label': _("Relecture (toutes formations)"),
            'order': 1,
        }, {
            'code': "review_before",
            'label': _("Relecture (avant approbation Conseil de composante)"),
            'order': 2,
        }, {
            'code': "review_after",
            'label': _("Relecture (MECC approuvées en Conseil de composante)"),
            'order': 3,
        }, {
            'code': "publish_all",
            'label': _('Publication (MECC validées CFVU)'),
            'order': 8,
        }])
        if 'DES1' in profiles_code:
            target.append({
                'code': "prepare_cfvu",
                'label': _("Préparation CFVU"),
                'order': 7,
            })
        else:
            target.append({
                'code': "prepare_cc",
                'label': _("Préparation Conseil de composante"),
                'order': 5,
            })

    data['university_year'] = UniversityYear.objects.get(
        code_year=currentyear().code_year)
    data['target'] = target
    return render(request, template, data)
