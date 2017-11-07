from ..degree.models import Degree, DegreeType
from ..files.models import FileUpload
from ..institute.models import Institute
from ..adm.models import MeccUser, Profile
from ..rules.models import Rule
from ..training.models import Training, SpecificParagraph
from ..years.models import InstituteYear, UniversityYear
from django.views.generic.list import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.utils.translation import ugettext as _
from django.shortcuts import render
from django_cas.decorators import login_required, user_passes_test
from mecc.decorators import is_ajax_request, is_post_request
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from mecc.decorators import group_required, profile_required, profile_or_group_required
from django.http import JsonResponse

@login_required
@group_required('DES1', 'VP')
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
    institutes_letters = FileUpload.objects.filter(object_id__in=institutes.values_list(
        'pk', flat=True), additional_type="letter_%s/%s" % (uy.code_year, uy.code_year + 1))
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

    derogations = SpecificParagraph.objects.filter(code_year=uy.code_year)

    topten_d = derogations.values('rule_gen_id').annotate(nb_derog=Count('rule_gen_id'), nb_cmp=Count(
        'training__supply_cmp', distinct=True)).order_by('-nb_derog').exclude(nb_cmp__isnull=True)

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
    data['topten_derog'] = topten_d[:10]

    for d in data['topten_derog']:
        d['rule'] = Rule.objects.get(id=d['rule_gen_id'])

    return render(request, template, data)


@login_required
#@group_required('DES1', 'RAC', 'DIRCOMP')
#@profile_required('ECI')
@profile_or_group_required(('DES1', 'RAC', 'DIRCOMP'), ('ECI'))
def institute_dashboard(request, code, template='dashboards/institute_dashboard.html'):
    data = {}
    supply_filter = []
    cfvu_entries = []
    trainings_data = []
    # objects needed
    uy = UniversityYear.objects.get(is_target_year=True)
    iy = InstituteYear.objects.filter(
        code_year=uy.code_year, date_expected_MECC__gt=uy.date_validation)

    institute = Institute.objects.get(code=code)
    iycmp = InstituteYear.objects.get(
        code_year=uy.code_year, id_cmp=institute.pk)

    for year in iy:
        cfvu_entries.append(dict(domain=institute.field.name,
                                 cmp=institute.label, date=year.date_expected_MECC))

    t = Training.objects.filter(code_year=uy.code_year, supply_cmp=code)
    t_eci = t.filter(MECC_type='E')
    t_cc_ct = t.filter(MECC_type='C')

    # get institutes who are supplier for a training
    for training in t:
        if training.supply_cmp in code:
            supply_filter.append(training.supply_cmp)

    doc_cadre = FileUpload.objects.get(object_id=uy.id)

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

    trainings_data = t.values('degree_type').annotate(t_count=Count('pk'))

    derogations = SpecificParagraph.objects.filter(
        training__supply_cmp=code, code_year=uy.code_year)

    topten_d = derogations.values('rule_gen_id').annotate(nb_derog=Count('rule_gen_id'), nb_formations=Count(
        'training__id', distinct=True))

    # set datas for view
    data['institute'] = institute
    data['trainings_counter'] = t.count()
    data['trainings_eci_counter'] = t_eci.count()
    data['trainings_cc_ct_counter'] = t_cc_ct.count()
    data['rules'] = rules
    data['rules_counter'] = rules.count()
    data['doc_cadre'] = doc_cadre
    data['university_year'] = uy
    data['university_year_cmp'] = iycmp
    data['cfvu_entries'] = cfvu_entries
    data['institute_cfvu_counter'] = iy.count()
    data['trainings_uncompleted_counter'] = t_uncompleted.count()
    data['trainings_completed_no_validation_counter'] = t_completed_no_validation.count()
    data['trainings_validated_des_waiting_counter'] = t_validated_des_waiting.count()
    data['trainings_validated_cfvu_waiting_counter'] = t_validated_cfvu_waiting.count()
    data['trainings_validated_cfvu_counter'] = t_validated_cfvu.count()
    data['institute_data'] = trainings_data
    data['trainings_eci_counter'] = t_eci.count()
    data['trainings_cc_ct_counter'] = t_cc_ct.count()
    data['topten_derog'] = topten_d
    data['first_cfvu'] = uy.date_expected

    for d in data['topten_derog']:
        d['rule'] = Rule.objects.get(id=d['rule_gen_id'])

    for td in trainings_data:
        td['degree_type_label'] = DegreeType.objects.get(id=td['degree_type'])
        td['t_eci_count'] = t_eci.filter(degree_type=td['degree_type']).count()
        td['t_cc_ct_count'] = t_cc_ct.filter(
            degree_type=td['degree_type']).count()

    return render(request, template, data)
