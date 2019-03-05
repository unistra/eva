"""
View for document generator 3000
"""
import json
import re

from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, FileResponse, Http404
from django.utils.translation import ugettext as _
from django.shortcuts import render, get_object_or_404, redirect
from django_cas.decorators import login_required
from django_celery_results.models import TaskResult
from django.conf import settings

from mecc.apps.files.models import FileUpload
from mecc.apps.institute.models import Institute
from mecc.apps.mecctable.models import StructureObject, ObjectsLink, Exam
from mecc.apps.utils.excel import MeccTable
from mecc.apps.utils.docx import docx_gen
from mecc.apps.utils.queries import currentyear
from mecc.apps.training.models import Training
from mecc.libs.storage.ceph import Ceph
from mecc.apps.years.models import UniversityYear, InstituteYear

from mecc.apps.rules.models import Rule
from mecc.apps.training.models import AdditionalParagraph, SpecificParagraph

from mecc.apps.utils.pdfs import setting_up_pdf, \
    canvas_for_preview_mecctable, \
    preview_mecctable_story, NumberedCanvas_landscape, \
    DocGenerator
from mecc.apps.utils.documents_generator import Document as Doc

from .tasks import \
    task_generate_pdf_model_a, \
    task_generate_pdf_model_b, \
    task_generate_pdf_model_c, \
    task_generate_pdf_model_d


@login_required
def generate(request):
    """
    Modèles A et B format doc
    """
    if request.GET.get('gen_type') == "doc":
        return Doc.generate(
            gen_type=request.GET.get('gen_type'),
            model=request.GET.get('model'),
            trainings=Training.objects.filter(id__in=request.GET.getlist('selected')),
            reference=request.GET.get('ref'),
        )
    """
    Format excel
    """
    if request.GET.get('gen_type') == 'excel':
        return Doc.generate(
            gen_type=request.GET.get('gen_type'),
            trainings=Training.objects.filter(
                id__in=request.GET.getlist('selected')
            ).order_by('degree_type__display_order', 'label'),
            year=request.GET.get('year', currentyear().code_year),
            reference=request.GET.get('ref')
        )
    """
    Format PDF
    """
    template = 'doc_generator/generated_pdf.html'
    trainings = request.GET.getlist('selected')
    data = {}
    if not trainings:
        """
        si aucune formation n'est passée dans la requête, cela veut dire que
        l'utilisateur demande un document modèle C (eci) ou D (historique des
        mecc validées).
        ces modèles sont des variantes du modèle A. leur comportement a été
        inclus dans la classe ModelA du générateur de documents
        """
        try:
            if request.GET.get('year') and re.match(r'2\d{3}', request.GET.get('year')):
                current_year = request.GET.get('year')
            else:
                current_year = currentyear().code_year
        except AttributeError:
            return render(
                request,
                'msg.html',
                {'msg': _("initialisation de l'année non effectuée")}
            )
        institute = Institute.objects.get(id=request.GET.get('institute'))
        trainings = Training.objects.filter(
            code_year=current_year,
            supply_cmp=institute.code,
            is_used=True
        )
        if request.GET.get('model') == 'd':
            """
            modèle D
            """
            task = task_generate_pdf_model_d.delay(
                user=(request.user.first_name, request.user.last_name),
                trainings=[training.id for training in trainings.filter(date_val_cfvu__isnull=False)],
                target=request.GET.get('target'),
                date=request.GET.get('date'),
                year=request.GET.get('year'),
            )
        else:
            """
            modèle C
            """
            trainings = trainings.filter(
                id__in=[training.id for training in trainings if training.is_ECI_MECC is True]
            )
            if trainings.count() == 0:
                data['back_url'] = "/training/list_all_meccs/"
                data['message'] = _("Aucune formation affichable.")
                return render(request, template, data)
            else:
                task = task_generate_pdf_model_c.delay(
                    user=(request.user.first_name, request.user.last_name),
                    trainings=[training.id for training in trainings],
                    date=request.GET.get('date')
                )
    """
    modèle A
    """
    if request.GET.get('model') == 'a':
        task = task_generate_pdf_model_a.delay(
            user=(request.user.first_name, request.user.last_name),
            trainings=request.GET.getlist('selected'),
            reference=request.GET.get('ref'),
            standard=request.GET.get('standard'),
            target=request.GET.get('target'),
            date=request.GET.get('date')
        )
    """
    modèle B
    """
    if request.GET.get('model') == 'b':
        task = task_generate_pdf_model_b.delay(
            user=(request.user.first_name, request.user.last_name),
            trainings=request.GET.getlist('selected'),
            reference=request.GET.get('ref'),
            standard=request.GET.get('standard'),
            target=request.GET.get('target'),
            date=request.GET.get('date')
        )

    task_result, created = TaskResult.objects.get_or_create(task_id=task.id)
    task_id = task_result.id
    return redirect('doc_gen:generate_pdf', task_id=task_id)

def generate_pdf(request, task_id, template='doc_generator/generated_pdf.html'):
    data = {'task_id': task_id}

    return render(request, template, data)

def get_pdf_task_status(request, task_id):
    task = TaskResult.objects.get(id=task_id)
    response = {'status': task.status}
    if task.status == 'SUCCESS':
        pdf_url = task.result.encode('utf-8').decode('unicode_escape')
        response['task_id'] = task_id
    return JsonResponse(response, safe=False)

def get_pdf(request, task_id):
    task = TaskResult.objects.get(id=task_id)
    filename = task.result

    try:
        return FileResponse(
            open(
                settings.MEDIA_ROOT+'/tmp/%s' % filename[1:-1],
                'rb'
            ), content_type='application/pdf'
        )

    except FileNotFoundError:
        raise Http404()

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
            trainings = trainings.filter(date_val_cfvu__isnull=False)
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
    institute_code = request.GET.get('institute')
    institute = Institute.objects.get(code=institute_code)
    json = True if request.GET.get('json') else False
    trainings = Training.objects.filter(
        code_year=current_year, supply_cmp=institute_code, is_used=True).order_by('degree_type', 'label')

    if institute.ROF_support:
        trainings = trainings.exclude(
            is_existing_rof=False,
        )
    else:
        trainings = trainings.exclude(
            is_existing_rof=False,
            degree_type__ROF_code='EA',
        )

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
    years = UniversityYear.objects \
        .filter(is_year_init=True) \
        .order_by('-code_year')
    return years


@login_required()
def history_home(request):
    try:
        current_year = currentyear().code_year
    except AttributeError:
        return render(request, 'msg.html',
                      {'msg': _("Initialisation de l'année non effectuée")})
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
            code_year=year, supply_cmp=institute.code, is_used=True, date_val_cfvu__isnull=False)
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
            'labelled': institute.label,
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


@login_required
def generate_excel_mecctable(request):
    year = request.GET.get('year', currentyear().code_year)
    references = request.GET.get('ref', 'with_si')  # ['without', 'with_si', 'with_rof', 'both']
    training_ids = request.GET.getlist('selected')
    trainings = Training.objects.filter(id__in=[e for e in training_ids]) \
        .order_by('degree_type__display_order', 'label')

    output = MeccTable().get_mecc_tables(trainings, year, references)

    doc_name = "eva_mecctable_%s" % year
    response = HttpResponse(
        output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % doc_name

    return response


@login_required
def generate_rules_docx(request):
    """
    Docx document generation
    """
    model = request.GET.get('model')
    reference = request.GET.get('ref')
    year = UniversityYear.objects.get(code_year=currentyear().code_year)
    institute = Institute.objects.get(code=request.GET.get('institute'))
    training_ids = request.GET.getlist('selected')
    trainings = Training.objects.filter(
        id__in=[training_id for training_id in training_ids]).order_by(
        'degree_type',
        'MECC_type',
        'label')
    data_degree_types = list(set([training.degree_type for training in trainings]))
    data = [model, reference, year, institute.label]
    for data_degree_type in data_degree_types:
        data_trainings = trainings.filter(degree_type=data_degree_type)
        data_mecc_types = list(set([training.MECC_type for training in data_trainings]))
        data.append({
            'degree_type': data_degree_type,
            'mecc_types': data_mecc_types,
            'trainings': data_trainings
        })

    docx_document = docx_gen(data)

    doc_name = "eva_rules_%s" % year
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="%s".docx' % doc_name
    docx_document.save(response)

    return response


@login_required()
def published_mecc(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    filename = '{year}/{id}-{ref_rof}.pdf'.format(
        year=training.code_year,
        id=training.id,
        ref_rof=training.ref_cpa_rof
    )
    pdf = Ceph(filename=filename).get_file()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
        filename.replace('/', '-')
    )
    response.write(pdf.getvalue())

    return response
