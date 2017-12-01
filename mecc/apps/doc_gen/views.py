"""
View for document generator 3000
"""
from django.utils.translation import ugettext as _
from django.shortcuts import render,  redirect
from django.http import JsonResponse

from mecc.apps.institute.models import Institute
from mecc.apps.mecctable.models import StructureObject
from mecc.apps.utils.queries import currentyear
from mecc.apps.training.models import Training
from mecc.apps.years.models import UniversityYear, InstituteYear


def home(request, template='doc_generator/home.html'):
    """
    Home screen for generator 3000
    """
    data = {}
    current_year = currentyear().code_year
    trainings = Training.objects.filter(code_year=current_year)
    all_institutes = Institute.objects.filter(
        code__in=[e.supply_cmp for e in trainings])
    profiles = request.user.meccuser.profile.all()
    institute_year = InstituteYear.objects.filter(
        code_year=current_year)
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
            'RESPFORM', 'RESPENS']) or request.user.is_superuser:
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
            'DES1', 'DIRCOMP', 'RAC', 'REFAPP', 'DIRETU', 'GESCOL']) or request.user.is_superuser:
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
        if 'DES1' in profiles_code or request.user.is_superuser:
            target.append({
                'code': "prepare_cfvu",
                'label': _("Préparation CFVU"),
                'order': 7,
            })
            if request.user.is_superuser:
                target.append({
                    'code': "prepare_cc",
                    'label': _("Préparation Conseil de composante"),
                    'order': 5,
                })
        else:
            target.append({
                'code': "prepare_cc",
                'label': _("Préparation Conseil de composante"),
                'order': 5,
            })

    data['university_year'] = UniversityYear.objects.get(
        code_year=current_year)
    data['target'] = sorted(target, key=lambda k: k['order'])

    # GET FIRST IN ORDER TO GET DISPLAY WHEN ARRIVING ON PAGE
    try:
        class FakeRequest(object):
            """
            Fake request to mock request GET
            """
            pass
        fake_request = FakeRequest()
        fake_request.GET = {
            'target': data['target'][0].get('code'),
            'institute': data['institutes'][0][0].code,
            # ''
        }
        fake_request.user = request.user
    except IndexError:
        data['trainings'] = None
        return render(request, template, data)

    data['trainings'] = trainings_for_target(fake_request)

    return render(request, template, data)


def trainings_for_target(request):
    """
    Return list of trainings according to target specificities, institute and
    year
    """
    current_year = currentyear().code_year
    target = request.GET.get('target')
    institute = request.GET.get('institute')
    json = True if request.GET.get('json') else False
    trainings = Training.objects.filter(
        code_year=current_year, institutes__code=institute)

    def process_review_all():
        return [e.small_dict for e in trainings]

    def process_review_before():
        return [e.small_dict for e in trainings if e.date_val_cmp in [
            '', ' ', None]]

    def process_review_after():
        return [e.small_dict for e in trainings if e.date_val_cmp not in [
            '', ' ', None]]

    def process_review_my():
        if request.user.is_superuser:
            return [e.small_dict for e in trainings]
        profiles = request.user.meccuser.profile.all()
        struct_object = StructureObject.objects.filter(
            code_year=current_year, RESPENS_id=request.user.username)
        spe_trainings = []
        if [e.cmp for e in profiles if e.code == 'RESPENS']:
            spe_trainings.extend(
                trainings.filter(code_year=current_year,
                                 id__in=[e.owner_training_id for e in struct_object]))
        if [e.cmp for e in profiles if e.code == 'RESPFORM']:
            spe_trainings.extend(
                trainings.filter(resp_formations=request.user.meccuser,
                                 code_year=current_year))

        return [e.small_dict for e in spe_trainings]

    def process_prepare_cc():
        return [e.small_dict for e in trainings if (
            e.progress_rule == 'A' and e.progress_table == 'A')]

    def process_prepare_cc_my():
        print("I'm here : process_prepare_cc_my")
        pass

    def process_prepare_cfvu():
        print("I'm here : process_prepare_cfvu")
        pass

    def process_publish_all():
        print("I'm here : process_publish_all")
        pass

    def process_publish_my():
        print("I'm here : process_publish_my")
        pass

    process = {
        'review_all': process_review_all,
        'review_before': process_review_before,
        'review_after': process_review_after,
        'review_my': process_review_my,
        'prepare_cc': process_prepare_cc,
        'prepare_cc_my': process_prepare_cc_my,
        'prepare_cfvu': process_prepare_cfvu,
        'publish_all': process_publish_all,
        'publish_my': process_publish_my,
    }

    trains = process[target]()
    print(trains)
    return JsonResponse(trains, safe=False) if json else trains
