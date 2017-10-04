from ..institute.models import Institute
from ..years.models import InstituteYear, UniversityYear
from ..degree.models import Degree
from ..training.models import Training
from ..files.models import FileUpload
from ..rules.models import Rule
from django.views.generic.list import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.utils.translation import ugettext as _
from django.shortcuts import render
from django_cas.decorators import login_required
from mecc.decorators import is_ajax_request, is_post_request
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from mecc.decorators import group_required
from django.http import JsonResponse


def general_dashboard(request, template='dashboards/general_dashboard.html'):
    data = {}
    supply_filter = []
    cfvu_entries = []
    # objects needed
    uy = UniversityYear.objects.get(is_target_year=True)
    iy = InstituteYear.objects.filter(code_year=uy.code_year, date_expected_MECC__gt=uy.date_validation)
    institutes = Institute.objects.filter(training__code_year=uy.code_year).distinct()

    for year in iy:
        inst = institutes.get(pk=year.id_cmp)
        cfvu_entries.append(dict(domain=inst.field.name,cmp=inst.label,date=year.date_expected_MECC))

    trainings = Training.objects.filter(code_year=uy.code_year)
    trainings_eci = trainings.filter(MECC_type='E')
    trainings_cc_ct = trainings.filter(MECC_type='C')

    # get institutes who are supplier for a training
    for training in trainings:
        if training.supply_cmp in institutes.values_list('code', flat=True):
            supply_filter.append(training.supply_cmp)

    supply_institutes = institutes.filter(code__in=supply_filter).distinct()
    doc_cadre = FileUpload.objects.get(object_id=uy.id)
    rules = Rule.objects.filter(code_year=uy.code_year).filter(is_edited__in=('O','X')).order_by('display_order')

    # set datas for view
    data['institutes_counter'] = supply_institutes.count()
    data['trainings_counter'] = trainings.count()
    data['trainings_eci_counter'] = trainings_eci.count()
    data['trainings_cc_ct_counter'] = trainings_cc_ct.count()
    data['institutes'] = supply_institutes
    data['rules'] = rules
    data['rules_counter'] = rules.count()
    data['doc_cadre'] = doc_cadre
    data['university_year'] = uy
    data['cfvu_entries'] = cfvu_entries
    data['institutes_cfvu_counter'] = iy.count()



    return render(request, template, data)
