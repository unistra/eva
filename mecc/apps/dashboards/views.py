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
    # objects needed
    uy = UniversityYear.objects.get(is_target_year=True)
    iy = InstituteYear.objects.filter(code_year=uy.code_year, date_expected_MECC__gt=uy.date_validation)
    institutes = Institute.objects.filter(training__code_year=uy.code_year).distinct() #.annotate(training=Count('training__pk'))
    trainings = Training.objects.filter(code_year=uy.code_year)
    trainings_eci = trainings.filter(MECC_type='E')
    trainings_cc_ct = trainings.filter(MECC_type='C')
    doc_cadre = FileUpload.objects.get(object_id=uy.id)
    rules = Rule.objects.filter(code_year=uy.code_year).filter(is_edited__in=('O','X')).order_by('display_order')
    # calculus
    institutes_counter = institutes.count()
    trainings_counter = trainings.count()
    trainings_eci_counter = trainings_eci.count()
    trainings_cc_ct_counter = trainings_cc_ct.count()
    rules_counter = rules.count()
    institutes_cfvu_counter = iy.count()
    # set datas for view
    data['institutes_counter'] = institutes_counter
    data['trainings_counter'] = trainings_counter
    data['trainings_eci_counter'] = trainings_eci_counter
    data['trainings_cc_ct_counter'] = trainings_cc_ct_counter
    data['institutes'] = institutes
    data['rules'] = rules
    data['rules_counter'] = rules_counter
    data['doc_cadre'] = doc_cadre
    data['university_year'] = uy
    data['institute_year'] = iy
    data['institutes_cfvu_counter'] = institutes_cfvu_counter



    return render(request, template, data)
