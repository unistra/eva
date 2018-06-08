"""
View for document generator 3000
"""
import json
import re

from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from django.shortcuts import render

from mecc.apps.files.models import FileUpload
from mecc.apps.institute.models import Institute
from mecc.apps.mecctable.models import StructureObject
from mecc.apps.utils.queries import currentyear
from mecc.apps.training.models import Training
from mecc.apps.years.models import UniversityYear, InstituteYear

from mecc.apps.rules.models import Rule
from mecc.apps.training.models import AdditionalParagraph, SpecificParagraph

from mecc.apps.utils.pdfs import setting_up_pdf, \
    canvas_for_preview_mecctable, \
    preview_mecctable_story, NumberedCanvas_landscape, \
    DocGenerator

from django_cas.decorators import login_required


@login_required
def generate_pdf(request, template='doc_generator/generated_pdf.html'):
    data = {'url': request.GET.urlencode()}
    return render(request, template, data)


@login_required
def dispatch_to_good_pdf(request):
    """
    Get ajax data and dispatch to correct pdf
    """
    # GET ALL INFORMATIONS
    trainings = request.GET.getlist('selected')
    generator = DocGenerator()

    if not trainings:
        try:
            if request.GET.get('year') and re.match(r'2\d{3}', request.GET.get('year')):
                current_year = request.GET.get('year')
            else:
                current_year = currentyear().code_year
        except AttributeError:
            return render(request, 'msg.html',
                          {'msg': _("Initialisation de l'année non effectuée")}
                          )
        institute = Institute.objects.get(id=request.GET.get('institute'))
        trainings = Training.objects.filter(
            code_year=current_year, supply_cmp=institute.code, is_used=True)

        if 'd' == request.GET.get('model'):
            doc, response = generator.validated_history(request, trainings, institute, current_year)
        else:
            doc, response = generator.create_eci(request, trainings)
    else:
        doc, response = generator.run(request, trainings)

    return response


@login_required
def preview_mecctable(request):
    """
    View getting all data to generate asked pdf
    """
    title = "PREVISUALISATION du TABLEAU"
    training = Training.objects.filter(
        id=request.GET.get('training_id')).first()
    full = None if not request.GET.get(
        'full') else True if 'yes' in request.GET.get('full') else False
    response, doc = setting_up_pdf(title, margin=32, portrait=False)
    if training:
        if full:
            additionals = AdditionalParagraph.objects.filter(
                training=training)
            specifics = SpecificParagraph.objects.filter(
                training=training)
            all_rules = Rule.objects.filter(
                degree_type=training.degree_type,
                code_year=training.code_year).distinct()

            story = preview_mecctable_story(
                training, [], True, model='a', additionals=additionals,
                specifics=specifics, edited_rules=all_rules, title=_(
                    'Prévisualisation des MECC'))
        else:
            story = preview_mecctable_story(training, title=_(
                'Prévisualisation du tableau'))
    else:
        story = []
    doc.build(
        story,
        onFirstPage=canvas_for_preview_mecctable,
        onLaterPages=canvas_for_preview_mecctable,
        canvasmaker=NumberedCanvas_landscape)
    return response


@login_required
def home(request, template='doc_generator/home.html'):
    """
    Home screen for generator 3000
    """
    data = {}

    try:
        current_year = currentyear().code_year
    except AttributeError:
        return render(request, 'msg.html',
                      {'msg': _("Initialisation de l'année non effectuée")})

    trainings = Training.objects.filter(code_year=current_year, is_used=True)
    all_institutes = Institute.objects.filter(
        code__in=[e.supply_cmp for e in trainings]).order_by('label')
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

    # GET FIRST IN ORDER TO GET DISPLAY WHEN ARRIVING ON PAGE
    try:
        class FakeRequest(object):
            """
            Fake request to mock request GET
            """
            user = request.user  # To avoid error due to @login_required
            pass

        fake_request = FakeRequest()
        fake_request.GET = {'institute': data['institutes'][
            0][0].code, 'user': request.user}

        data['target'] = available_target(fake_request)
        fake_request.GET.update({'target': data['target'][0].get('code'), })

    except IndexError:
        data['trainings'] = None
        return render(request, template, data)

    data['trainings'] = json.dumps(trainings_for_target(fake_request))

    data['university_year'] = UniversityYear.objects.get(
        code_year=current_year)

    return render(request, template, data)


@login_required
def available_target(request):
    """
    Return list of target according to user and selected institute
    """
    json = True if request.GET.get('json') else False

    target = []
    cmp_code = request.GET.get('institute')
    user = User.objects.get(username=request.GET.get('user'))
    # Handling profiles
    p = user.meccuser.profile.all()
    other = [{'code': "DES1" if 'DES1' in [e.name for e in user.groups.all()]
    else '', 'cmp:': "ALL"}]
    profiles = [{'code': e.code, 'cmp': e.cmp} for e in p if p]
    profiles.extend(other)

    DES1 = any(True for profile in profiles if profile.get('code') == "DES1")
    profile_cmp = [e.get('code') for e in profiles if e.get('cmp') == cmp_code]

    if any(True for profile in profile_cmp if profile in [
        'RESPFORM', 'RESPENS']) or user.is_superuser:
        target.append({
            'code': "review_my",
            'label': _("Relecture (mes formations)"),
            'order': 4,
        })
        if 'RESPENS' not in profile_cmp:
            target.extend([{
                'code': "prepare_cc_my",
                'label': _("Préparation Conseil de composante (mes formations)"),
                'order': 6,
            }, {
                'code': "publish_my",
                'label': _("Publication (mes formations validées en CFVU)"),
                'order': 9,
            }])

    if any(True for profile in profile_cmp if profile in [
        'DIRCOMP', 'RAC', 'REFAPP', 'DIRETU', 'GESCOL'
    ]) or user.is_superuser or DES1:
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
        if DES1 or user.is_superuser:
            target.append({
                'code': "prepare_cfvu",
                'label': _("Préparation CFVU"),
                'order': 7,
            })
            if user.is_superuser:
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

    sorted_target = sorted(target, key=lambda k: k['order'])
    # if True:
    #     request.GET.update({'target': sorted_target[0].get('code')})
    #     trainings_for_target(request)
    #     return sorted_target
    # else:
    return JsonResponse(sorted_target, safe=False) if json else sorted_target


@login_required
def trainings_for_target(request):
    """
    Return list of trainings according to target specificities, institute and
    year
    """
    current_year = currentyear().code_year
    user = User.objects.get(username=request.GET.get('user'))

    target = request.GET.get('target')
    institute = request.GET.get('institute')
    json = True if request.GET.get('json') else False
    trainings = Training.objects.filter(
        code_year=current_year, supply_cmp=institute, is_used=True).order_by('degree_type', 'label')

    profiles = user.meccuser.profile.all()

    def process_review_all():
        return [e.small_dict for e in trainings]

    def process_review_before():
        return [e.small_dict for e in trainings if e.date_val_cmp in [
            '', ' ', None]]

    def process_review_after():
        return [e.small_dict for e in trainings if e.date_val_cmp not in [
            '', ' ', None]]

    def process_review_my():
        struct_object = StructureObject.objects.filter(
            code_year=current_year, RESPENS_id=user.username)
        spe_trainings = []
        if [e.cmp for e in profiles if e.code == 'RESPENS']:
            spe_trainings.extend(
                trainings.filter(code_year=current_year,
                                 id__in=[e.owner_training_id for e in struct_object]))
        if [e.cmp for e in profiles if e.code == 'RESPFORM']:
            spe_trainings.extend(
                trainings.filter(resp_formations=user.meccuser,
                                 code_year=current_year))

        return [e.small_dict for e in spe_trainings]

    def process_prepare_cc():
        return [e.small_dict for e in trainings if (
                e.progress_rule == 'A' and e.progress_table == 'A')]

    def process_prepare_cc_my():
        spe_train = trainings.filter(
            resp_formations=user.meccuser, code_year=current_year)
        return [e.small_dict for e in spe_train if (
                e.progress_rule == 'A' and e.progress_table == 'A')]

    def process_prepare_cfvu():
        return [e.small_dict for e in trainings if e.date_visa_des not in [
            '', ' ', None]]

    def process_publish_all():
        return [e.small_dict for e in trainings if e.date_val_cfvu not in [
            '', ' ', None]]

    def process_publish_my():
        spe_train = trainings.filter(
            resp_formations=user.meccuser, code_year=current_year)
        return [e.small_dict for e in spe_train if e.date_val_cfvu not in [
            '', ' ', None]]

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
    return JsonResponse(trains, safe=False) if json else trains


def get_years(current_year):
    """Get years for select box"""
    years = UniversityYear.objects\
        .filter(is_year_init=True) \
        .order_by('-code_year')
    return years


@login_required()
def history_home(request):
    current_year = currentyear().code_year
    years = get_years(current_year)

    return render(request, 'doc_generator/history_home.html', {
        'active_years': years,
        'home': True,
    })


@login_required()
def history_for_year(request, year):
    """
    List of Institutes for given year with links to MECC, presentation letter
    and other documents
    :param request:
    :param year:
    :return:
    """

    def get_trainings_for_institute_and_year(institute):
        trainings = Training.objects.filter(
            code_year=year, supply_cmp=institute.code, is_used=True)
        if trainings.count():
            return trainings.count()
        return False

    def get_institutes():
        active_institutes_for_year = InstituteYear.objects.filter(code_year=year)
        institutes = Institute.objects.filter(
            id__in=active_institutes_for_year.values_list('id_cmp', flat=True).distinct()
        ).order_by('field', 'label')
        return institutes


    current_year = currentyear().code_year
    selected_year = year
    years = get_years(current_year)
    institutes = get_institutes()
    ordered_list = []
    for institute in institutes:
        try:
            iy = InstituteYear.objects.get(
                code_year=selected_year, id_cmp=institute.id)
        except ObjectDoesNotExist:
            continue
        except MultipleObjectsReturned:
            iy = InstituteYear.objects.filter(
                code_year=selected_year, id_cmp=institute.id).first()
        field = {
            'id': institute.id,
            'year': year,
            'domaine': institute.field.name,
            'code': institute.code,
            'labelled': "%s - %s" % (institute.label, institute.ROF_code)
            if institute.ROF_code not in ['', ' ', None] else institute.label,
            'mecc': get_trainings_for_institute_and_year(institute),
            'letter': FileUpload.objects.filter(
                object_id=institute.id,
                additional_type__startswith='letter_' + selected_year),
            'misc_docs': FileUpload.objects.filter(
                object_id=institute.id,
                additional_type__startswith='misc_' + selected_year).order_by('file'),
        }
        if field['mecc'] or field['letter'] or field['misc_docs']:
            ordered_list.append(field)

    return render(request, 'doc_generator/history_home.html', {
        'active_years': years,
        'selected_year': str(selected_year),
        'institutes': ordered_list,
    })
