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
    institutes_data = []
    # objects needed
    uy = UniversityYear.objects.get(is_target_year=True)
    iy = InstituteYear.objects.filter(
        code_year=uy.code_year, date_expected_MECC__gt=uy.date_validation)
    institutes = Institute.objects.filter(
        training__code_year=uy.code_year).distinct()

    for year in iy:
        inst = institutes.get(pk=year.id_cmp)
        cfvu_entries.append(dict(domain=inst.field.name,
                                 cmp=inst.label, date=year.date_expected_MECC))

    t = Training.objects.filter(code_year=uy.code_year)
    t_eci = t.filter(MECC_type='E')
    t_cc_ct = t.filter(MECC_type='C')

    # get institutes who are supplier for a training
    for training in t:
        if training.supply_cmp in institutes.values_list('code', flat=True):
            supply_filter.append(training.supply_cmp)

    supply_institutes = institutes.filter(code__in=supply_filter).distinct()
    doc_cadre = FileUpload.objects.get(object_id=uy.id)
    institutes_letters = FileUpload.objects.filter(object_id__in=institutes.values_list('pk', flat=True), additional_type="letter_%s/%s" % (uy.code_year, uy.code_year+1))

    rules = Rule.objects.filter(code_year=uy.code_year).filter(
        is_edited__in=('O', 'X')).order_by('display_order')

    t_uncompleted = t.filter(progress_rule="E") | t.filter(progress_table="E")
    t_completed_no_validation = t.filter(
        progress_rule="A", progress_table="A", date_val_cmp__isnull=True)
    t_validated_des_waiting = t.filter(
        date_val_cmp__isnull=False, date_visa_des__isnull=True)
    t_validated_no_cfvu_waiting = t.filter(
        date_val_cmp__isnull=True) | t.filter(date_visa_des__isnull=True)
    t_validated_cfvu_waiting = t.filter(
        date_val_cmp__isnull=False, date_visa_des__isnull=False, date_val_cfvu__isnull=True)
    t_validated_cfvu = t.filter(date_val_cfvu__isnull=False)

    institutes_trainings_completed_no_validation = institutes.filter(code__in=t_completed_no_validation.values_list(
        'supply_cmp', flat=True)).exclude(code__in=t_uncompleted.values_list('supply_cmp', flat=True))
    institutes_trainings_waiting_cfvu = institutes.filter(code__in=t_validated_cfvu_waiting.values_list(
        'supply_cmp', flat=True)).exclude(code__in=t_validated_no_cfvu_waiting.values_list('supply_cmp', flat=True))

    for s in supply_institutes:
        institutes_data.append(dict(institute=s.label,
                                    t_count=t.filter(
                                        supply_cmp=s.code).count(),
                                    t_uncompleted_count=t_uncompleted.filter(
                                        supply_cmp=s.code).count(),
                                    t_completed_no_val_count=t_completed_no_validation.filter(
                                        supply_cmp=s.code).count(),
                                    t_validated_des_waiting_count=t_validated_des_waiting.filter(
                                        supply_cmp=s.code).count(),
                                    t_validated_cfvu_waiting_count=t_validated_cfvu_waiting.filter(
                                        supply_cmp=s.code).count(),
                                    t_validated_cfvu_count=t_validated_cfvu.filter(
                                        supply_cmp=s.code).count(),
                                    ))

    # set datas for view
    data['institutes_counter'] = supply_institutes.count()
    data['trainings_counter'] = t.count()
    data['trainings_eci_counter'] = t_eci.count()
    data['trainings_cc_ct_counter'] = t_cc_ct.count()
    data['institutes'] = supply_institutes
    data['rules'] = rules
    data['rules_counter'] = rules.count()
    data['doc_cadre'] = doc_cadre
    data['university_year'] = uy
    data['cfvu_entries'] = cfvu_entries
    data['institutes_cfvu_counter'] = iy.count()
    data['trainings_uncompleted_counter'] = t_uncompleted.count()
    data['trainings_completed_no_validation_counter'] = t_completed_no_validation.count()
    data['institutes_trainings_completed_no_validation'] = institutes_trainings_completed_no_validation
    data['institutes_trainings_completed_no_validation_counter'] = institutes_trainings_completed_no_validation.count()
    data['trainings_validated_des_waiting_counter'] = t_validated_des_waiting.count()
    data['trainings_validated_cfvu_waiting_counter'] = t_validated_cfvu_waiting.count()
    data['trainings_validated_cfvu_counter'] = t_validated_cfvu.count()
    data['institutes_trainings_waiting_cfvu'] = institutes_trainings_waiting_cfvu
    data['institutes_trainings_waiting_cfvu_counter'] = institutes_trainings_waiting_cfvu.count()
    data['institutes_data'] = institutes_data
    data['institutes_letters'] = institutes_letters
    data['institutes_letters_counter'] = institutes_letters.count()
    data['top_ten_count'] = range(1,11)

    return render(request, template, data)
