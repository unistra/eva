# -*- coding: UTF-8 -*-
import json
import logging
from decimal import InvalidOperation

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, ListView, UpdateView, CreateView
from django_cas.decorators import login_required

from mecc.apps.adm.models import MeccUser, Profile
from mecc.apps.institute.models import Institute
from mecc.apps.training.models import Training
from mecc.apps.utils.documents_generator import Document
from mecc.apps.utils.manage_pple import is_poweruser
from mecc.apps.utils.queries import currentyear, get_mecc_table_order
from mecc.apps.utils.ws import get_user_from_ldap
from mecc.decorators import is_post_request, is_ajax_request
from .forms import StructureObjectForm, ObjectsLinkForm, ExamForm
from .models import StructureObject, ObjectsLink, Exam

LOGGER = logging.getLogger(__name__)


def has_exams(request):
    """
    Returns "true" or "false" whether a structure has or not exams attached.
    """
    structure_id = request.GET.get('structure_id')
    if Exam.objects.filter(id_attached=structure_id):
        return JsonResponse({'has_exams': 1})
    else:
        return JsonResponse({'has_exams': 0})


def copy_exam_1_to_2(request, id_structure):
    """
    Copy primary exam to secondary exams
    """
    structure_concerned = StructureObject.objects.get(id=id_structure)
    exams = Exam.objects.filter(
        id_attached=structure_concerned.id, code_year=currentyear().code_year)
    exams_1 = exams.filter(session='1')
    exams_2 = exams.filter(session='2')
    id_auto_2 = [ex._id for ex in exams_2]
    for exam in exams_1:
        if exam._id not in id_auto_2:
            if exam.regime == "C":
                exam.type_ccct = "T"
            exam.pk = None
            exam.session = "2"
            exam.save()

    return JsonResponse({"status": 200})


def add_exam(request):
    """
    return json with added exam
    """
    # Get concerned training
    structure = StructureObject.objects.get(
        id=request.POST.get('id_structure'))
    # Get object (as a string)
    exam = request.POST.get('exam')
    # Convert it in dict
    obj = json.loads(exam)
    for e in obj:
        obj[e] = None if obj[e] == '' else obj[e]
    try:
        times = obj.get('exam_duration').split(':')
    except Exception:
        times = [None, None]
    part_h = times[0]

    try:
        part_m = times[1]
    except Exception:
        part_m = None

    try:
        exam = Exam.objects.create(
            code_year=currentyear().code_year,
            id_attached=request.POST.get('id_structure'),
            session='2' if request.POST.get('session2') else '1',
            regime=structure.regime,
            type_exam=obj.get('type_exam'),
            label=obj.get('label'),
            additionnal_info=obj.get('additionnal_info'),
            exam_duration_h=part_h,
            exam_duration_m=part_m if part_m else 0,
            convocation="O" if obj.get('convocation') else "N",
            type_ccct=obj.get('type_ccct'),
            eliminatory_grade=obj.get('eliminatory_grade'),
            is_session_2=obj.get('is_session_2'),
            threshold_session_2=obj.get('threshold_session_2'),
            coefficient=obj.get('coefficient')
        )
    except Exception as e:
        LOGGER.error('ADD EXAM ERROR__: \n{error}'.format(error=e))

    return JsonResponse({"status": 200})


def update_exam(request, id_structure):
    """
    return json with updated exam
    """
    exams = Exam.objects.filter(
        id_attached=id_structure, code_year=currentyear().code_year)
    obj = json.loads(request.POST.get('exam'))
    non_updated_exam = exams.get(id=obj.get('id'))
    non_updated_exam.delete()

    # Handling duration field
    time = obj.pop('exam_duration')
    for delim in ':h':
        time = time.replace(delim, ' ')
    times = time.split()
    try:
        part_h = times[0]
    except IndexError:
        part_h = None
    try:
        part_m = times[1]
    except IndexError:
        part_m = None

    obj['exam_duration_h'] = part_h
    obj['exam_duration_m'] = part_m

    s2 = obj.pop("convocation")
    obj['convocation'] = "O" if s2 else "N"

    for e in obj:
        obj[e] = None if obj[e] == '' else obj[e]
    try:
        Exam.objects.create(**obj)
    except Exception as e:
        LOGGER.error(
            'CANNOT Create exam in update_exam : \n{error}'.format(error=e))
    return JsonResponse({"status": 200})


def delete_exam(request, id_structure):
    """
    return json with confirmation of deleted exam
    """
    exams = Exam.objects.filter(
        id_attached=id_structure, code_year=currentyear().code_year)
    obj = json.loads(request.POST.get('exam'))
    to_del = exams.get(id=obj.get('id'))
    to_del.delete()
    return JsonResponse({"status": 200})


def list_exams(request, id_structure):
    """
    return json with all exam of a structure
    """
    structure_concerned = StructureObject.objects.get(id=id_structure)
    exams = Exam.objects.filter(
        id_attached=structure_concerned.id, code_year=currentyear().code_year).order_by('_id')
    if request.GET.get('session2') == 'True':
        asked_exams = exams.filter(session='2')
    else:
        asked_exams = exams.filter(session='1')

    return JsonResponse([e.as_json for e in asked_exams], safe=False)


def copy_old_exams(request, id_structure=None):
    """
    Copy exams from last year
    into unchanged structures owned by the current training
    """

    def copy_last_year_exams(structure):
        """
        Copy last year exams for the given structure
        """
        try:
            old_structure = StructureObject.objects.get(
                auto_id=structure.auto_id,
                code_year=structure.code_year-1
            )
            old_exams = Exam.objects.filter(
                id_attached=old_structure.id,
            )
            copied_exams = []
            if old_exams:
                old_exams_1 = old_exams.filter(session='1')
                old_exams_2 = old_exams.filter(session='2')
                import copy
                for old_exam_1 in old_exams_1:
                    exam_1 = copy.copy(old_exam_1)
                    exam_1.id = exam_1._id = None
                    exam_1.code_year = structure.code_year
                    exam_1.id_attached = structure.id
                    exam_1.save()
                    if old_exams_2 and \
                            old_exam_1._id in [old_exam_2._id for old_exam_2 in old_exams_2]:
                        copied_exams.append((old_exam_1._id, exam_1._id))

                for old_exam_2 in old_exams_2:
                    exam_2 = copy.copy(old_exam_2)
                    exam_2.id = exam_2._id = None
                    for old_exam_1_auto_id, exam_1_auto_id in copied_exams:
                        if old_exam_2._id == old_exam_1_auto_id:
                            exam_2._id = exam_1_auto_id
                    exam_2.code_year = structure.code_year
                    exam_2.id_attached = structure.id
                    exam_2.save()

                return 666
            else:
                return 333
        except StructureObject.DoesNotExist:
            return 999

    id_structure = request.GET.get('structure_id')
    data = {}
    data['exams_infos'] = {}
    if id_structure is not None:
        current_structure = StructureObject.objects.get(id=id_structure)
        data['exams_infos']['object'] = {
            'id_struct': current_structure.id,
            'st_label': current_structure.label,
            'st_nature': current_structure.nature,
            'st_regime': current_structure.regime,
            'st_session': current_structure.session,
            'st_ref_scol': current_structure.ref_si_scol,
            'st_rof_ref': current_structure.ROF_ref,
            'st_is_exam_template': current_structure.is_exam_template,
            'st_exam_template_label': current_structure.exam_template_label,
        }

        data['status'] = status = copy_last_year_exams(current_structure)

        if status == 666:
            data['msg'] = "Les épreuves de l'année précédente ont bien été importées."
        elif status == 333:
            data['msg'] = "Aucune épreuve à importer."
        else:
            data['msg'] = "Cette structure d'enseignement n'existait pas l'année précédente."

    else:
        id_training = request.GET.get('training_id')
        current_structures = StructureObject.objects.filter(
            owner_training_id=id_training,
        ).exclude(id__in=[exam.id_attached for exam in Exam.objects.filter(
            code_year=currentyear().code_year)])

        updated_objects = 0

        # we check that the corresponding current structure is empty
        # in that case, the old_exam is copied in the current_structure
        for structure in current_structures:
            if copy_last_year_exams(structure) == 666:
                updated_objects += 1
                data['exams_infos']['object_'+str(updated_objects)] = {
                    'id_struct': structure.id,
                    'st_label': structure.label,
                    'st_nature': structure.nature,
                    'st_regime': structure.regime,
                    'st_session': structure.session,
                    'st_ref_scol': structure.ref_si_scol,
                    'st_rof_ref': structure.ROF_ref,
                    'st_is_exam_template': structure.is_exam_template,
                    'st_exam_template_label': structure.exam_template_label,
                }
        data['updated_objects'] = updated_objects

    return JsonResponse(data)


@login_required
@is_ajax_request
def delete_exam_template(request):
    """
    Remove flag making a StructureObject a template for exams
    """
    try:
        structure_object_id = request.POST.get('structure_object_id')
        structure_object = StructureObject.objects.get(id=structure_object_id)
        structure_object.is_exam_template = False
        structure_object.exam_template_label = None
        structure_object.save()
        result = {
            'response': {
                'status': True,
            },
            'code': 200,
        }
    except Exception as e:
        result = {
            'response': {
                'status': False,
                'error': e,
            },
            'code': 500,
        }

    return JsonResponse(result['response'], status=result['code'])


@login_required
@is_ajax_request
def create_exam_template(request):
    """
    Mark a StructureObject as a template for exams
    """
    try:
        structure_object_id = request.POST.get('structure_object_id')
        exam_template_label = request.POST.get('exam_template_label').strip()
        structure_object = StructureObject.objects.get(id=structure_object_id)
        structure_object.is_exam_template = True
        structure_object.exam_template_label = exam_template_label
        structure_object.save()
        result = {
            'response': {
                'status': True,
            },
            'code': 200,
        }
    except Exception as e:
        result = {
            'response': {
                'status': False,
                'error': e,
            },
            'code': 500,
        }

    return JsonResponse(result['response'], status=result['code'])


@login_required
@is_ajax_request
def edit_exam_template(request):
    """
    Update the label describing an exam template
    """
    try:
        structure_object_id = request.POST.get('structure_object_id')
        exam_template_label = request.POST.get('exam_template_label').strip()
        structure_object = StructureObject.objects.get(id=structure_object_id)
        structure_object.exam_template_label = exam_template_label
        structure_object.save()
        result = {
            'response': {
                'status': True,
            },
            'code': 200,
        }
    except Exception as e:
        result = {
            'response': {
                'status': False,
                'error': e,
            },
            'code': 500,
        }

    return JsonResponse(result['response'], status=result['code'])


@login_required
@is_ajax_request
def exam_template_info(request):
    """
    Get exam template info for given StructureObject
    """
    structure_object_id = request.GET.get('structure_object_id')
    structure_object = StructureObject.objects.get(id=structure_object_id)

    return JsonResponse({
        'is_exam_template': structure_object.is_exam_template,
        'exam_template_label': structure_object.exam_template_label
    })


@login_required
@is_ajax_request
def list_exam_templates(request):
    """
    Get a list of all exam templates that can be applied to StructureObject
    (same Institute, Year and Regime)
    :param request:
    """
    structure_object_id = request.GET.get('structure_object_id')
    template_structure_object = StructureObject.objects.get(id=structure_object_id)

    institute = template_structure_object.cmp_supply_id
    regime = template_structure_object.regime
    session = template_structure_object.session
    year = template_structure_object.code_year

    templates = StructureObject.objects.filter(
        is_exam_template=True,
        cmp_supply_id=institute,
        code_year=year,
        regime=regime,
        session=session,
    ).exclude(
        id=structure_object_id,
    )

    result = []
    for template in templates:
        training = Training.objects.get(id=template.owner_training_id)
        result.append({
            'id': template.id,
            'label': template.exam_template_label,
            'nature': template.nature,
            'structure_object_label': template.label,
            'training_label': training.label,
            'regime': template.get_regime_display(),
            'session': template.get_session_display(),
        })

    return JsonResponse(result, safe=False)


@login_required
@is_ajax_request
def apply_exam_template(request):
    result = {}
    id_table = {}
    source_structure_object = StructureObject.objects.get(
        id=request.POST.get('source_structure_object_id')
    )
    destination_structure_object = StructureObject.objects.get(
        id=request.POST.get('destination_structure_object_id')
    )

    source_exams = Exam.objects.filter(id_attached=source_structure_object.id, code_year=currentyear().code_year)

    for source_exam in source_exams:
        auto_id = None
        try:
            if source_exam._id in id_table:
                auto_id = id_table[source_exam._id]  # exam._id can be the same in session 1 and session 2
            exam = Exam.objects.create(
                code_year=source_exam.code_year,
                id_attached=destination_structure_object.id,
                session=source_exam.session,
                _id=auto_id,
                regime=source_exam.regime,
                type_exam=source_exam.type_exam,
                label=source_exam.label,
                additionnal_info=source_exam.additionnal_info,
                exam_duration_h=source_exam.exam_duration_h,
                exam_duration_m=source_exam.exam_duration_m,
                convocation=source_exam.convocation,
                type_ccct=source_exam.type_ccct,
                eliminatory_grade=source_exam.eliminatory_grade,
                is_session_2=source_exam.is_session_2,
                threshold_session_2=source_exam.threshold_session_2,
                coefficient=source_exam.coefficient,
            )
            id_table[source_exam._id] = exam._id
        except Exception as e:
            LOGGER.error('COPY EXAM ERROR__: \n{error}'.format(error=e))

    return JsonResponse(result)


@login_required
def import_objectslink(request):
    """
    Create objectslink with selected structureobject
    """
    try:
        id_training = request.POST.get('id_training')
        id_parent = request.POST.get('asking_id')
        current_year = currentyear().code_year
        selected_id = [e for e in map(int, request.POST.getlist(
            'selected_id[]'))]
        object_link_list = ObjectsLink.objects.filter(
            id_child__in=[e for e in selected_id],
            code_year=current_year).exclude(is_imported=True)
        # based on id_child and **not** imported objectlink in
        # order to retrieve the original one :)
        not_imported = False
        for e in object_link_list:
            childs = ObjectsLink.objects.filter(
                code_year=current_year, id_parent=id_parent,
                id_training=id_training)
            order_in_child = childs.count() + 1
            if e.id_child not in [c.id_child for c in childs]:

                ObjectsLink.objects.get_or_create(
                    code_year=current_year,
                    id_training=id_training,
                    id_parent=id_parent,
                    id_child=e.id_child,
                    n_train_child=e.n_train_child,
                    nature_child="EXT",
                    order_in_child=order_in_child,
                    is_imported=True,
                    coefficient=e.coefficient,
                    eliminatory_grade=e.eliminatory_grade
                )
            else:
                not_imported = True
    except Exception as e:  # This is bad...
        print(e)
        return JsonResponse({"error": e})
    return JsonResponse({
        "status": 200, "not_imported": not_imported
    })


@is_ajax_request
def get_consom(request):
    """
    Give consumer of a certain imported object
    """
    so = StructureObject.objects.get(id=request.GET.get('id_obj'))
    lo = ObjectsLink.objects.filter(id_child=so.id, is_imported=True)
    structs = StructureObject.objects.filter(id__in=[e.id_parent for e in lo])
    trainings = Training.objects.filter(id__in=[e.id_training for e in lo])
    t = []
    for e in lo:
        training = trainings.get(id=e.id_training)
        a = {
            'code': training.supply_cmp,
            'label': training.label,
            'used': structs.get(
                id=e.id_parent).label if e.id_parent != 0 else _('Racine'),
            'respens': [{
                'first_name': r.user.first_name,
                'last_name': r.user.last_name,
                'mail': r.user.email
            } for r in training.resp_formations.all()]
        }
        t.append(a)

    return JsonResponse({
        'has_consom': True if lo else False,
        'year': "%s/%s" % (so.code_year, so.code_year + 1),
        'structure': {
            'label': so.label,
            'nature': so.nature,
            'si_scol': so.ref_si_scol,
            'rof': so.ROF_ref},
        'trainings': t if len(t) > 0 else 0,
        'status': 200})


@is_ajax_request
def get_owner(request):
    """
    Give infos on the training that owns a certain imported object
    """
    structure = StructureObject.objects.get(id=request.GET.get('id_obj'))
    owner = Training.objects.get(id=structure.owner_training_id)

    return JsonResponse({
        'year': "%s/%s" % (structure.code_year, structure.code_year+1),
        'structure': {
            'label': structure.label,
            'nature': structure.nature,
            'si_scol': structure.ref_si_scol,
            'rof': structure.ROF_ref,
        },
        'owner': {
            'code': owner.supply_cmp,
            'label': owner.label,
            'respforms': [{
                'first_name': respens.user.first_name,
                'last_name': respens.user.last_name
            } for respens in owner.resp_formations.all()],
        }
    })


@login_required
@is_ajax_request
def get_mutual_by_cmp(request):
    """
    Give list of suggested cmp according by
    """
    data = []
    try:
        asking = StructureObject.objects.get(
            id=request.GET.get('asking_id')) if request.GET.get(
            'asking_id') is not '0' else None
        asking_period = asking.period if asking else None
        cmp_code = request.GET.get('cmp_code')
        cmp_with_rof_support_ids = Institute.objects.filter(ROF_support=True).values_list('code', flat=True)
        data = {}
        try:
            if asking.nature == "SE":
                to_exclude = ["SE"]
            elif asking.nature in ["UE", "EC"]:
                to_exclude = ["UE", "SE"]
            else:
                to_exclude = [""]
        except AttributeError as e:  # when asking from root
            to_exclude = [""]
        s_list = StructureObject.objects.filter(
            cmp_supply_id=cmp_code,
            mutual=True,
            code_year=currentyear().code_year,
            is_in_use=True,
        ).exclude(
            nature__in=to_exclude,
        )
        if asking is not None:
            s_list = s_list.exclude(
                id=asking.id,
            )

        if asking_period and asking_period in ['I', 'P']:
            s_list = s_list.filter(period__in=[asking_period, 'A'])
        mutual_list = []
        for structure_object in s_list:
            training = Training.objects.get(id=structure_object.owner_training_id)

            if structure_object.is_existing_rof is False and structure_object.cmp_supply_id in cmp_with_rof_support_ids:
                continue
            if structure_object.is_existing_rof is False and training.degree_type.ROF_code == 'EA':
                continue

            mutual_list.append([
                "<input name='suggest-id' value='%s' type='checkbox'>" % (structure_object.id),
                structure_object.nature,
                structure_object.label,
                training.label,
                structure_object.get_regime_display(),
                structure_object.get_session_display(),
                structure_object.ECTS_credit,
                structure_object.external_name if structure_object.external_name else structure_object.get_respens_name,
                structure_object.ref_si_scol,
                structure_object.ROF_ref
            ])

        data['suggest'] = mutual_list
    except Exception as e:
        LOGGER.error('CANNOT GET mutual : \n{error}'.format(error=e))

    return JsonResponse(data)


@login_required
@is_ajax_request
@is_post_request
def update_grade_coeff(request):
    """
    Ajax view to update grade and coeff
    """
    val = strip_tags(request.POST.get('value'))
    to_update = request.POST.get('to_update')
    type_to_update = to_update.split('-')[-1]
    id_to_update = to_update.split('-')[0]
    link = ObjectsLink.objects.get(id=id_to_update)
    training = Training.objects.get(id=link.id_training)

    def update_recup_atb_ens(oldvalue, newvalue, type):
        if oldvalue is not None:
            if type == 'coeff':
                oldvalue = float(oldvalue)
            elif type == 'grade':
                oldvalue = int(oldvalue)
        if oldvalue != newvalue:
            if training.recup_atb_ens is False:
                training.recup_atb_ens = True
                training.save()

    if type_to_update == "coeff":
        old_coeff = link.coefficient
        if "nbsp" in val or val in ['', ' ', '&nbsp;', '&nbsp;&nbsp;']:
            link.coefficient = None
            link.save()
            update_recup_atb_ens(old_coeff, link.coefficient, 'coeff')
            return JsonResponse({"status": 'OK', "val": ""})
        try:
            link.coefficient = float(val.replace(",", "."))
            link.save()
            update_recup_atb_ens(old_coeff, link.coefficient, 'coeff')
            value = '{0:.2f}'.format(link.coefficient).replace(".", ",")
        except (ValueError, InvalidOperation) as e:
            if "ValueError" in e.__class__.__name__:
                text = _("Veuillez entrer un nombre")
            if "InvalidOperation" in e.__class__.__name__:
                text = _('Veuillez verifier votre saisie')
            return JsonResponse({
                "status": 'ERROR',
                "val": old_coeff,
                "error": text
            })
    if type_to_update == "grade":
        old_grade = link.eliminatory_grade
        try:
            if int(val) < 0 or int(val) > 20:
                return JsonResponse({
                    "status": 'ERROR',
                    "val": old_grade,
                    "error": _("Veuillez entrer une note comprise\
                     entre 0 et 20")
                })
            link.eliminatory_grade = int(val)
            link.save()
            update_recup_atb_ens(old_grade, link.eliminatory_grade, 'grade')
            value = link.eliminatory_grade
        except ValueError:
            if "nbsp" in val or val in ['', ' ', '&nbsp;', '&nbsp;&nbsp;']:
                link.eliminatory_grade = None
                link.save()
                update_recup_atb_ens(old_grade, link.eliminatory_grade, 'grade')
                return JsonResponse({"status": 'OK', "val": ''})
            return JsonResponse({
                "status": 'ERROR',
                "val": old_grade,
                "error": _("Veuillez entrer un nombre entier")
            })
    return JsonResponse({"status": 'OK', "val": value})


@login_required
@is_ajax_request
def get_stuct_obj_details(request):
    """
    Get details of structure, if it DoesNotExist return empty fields
    """
    training = Training.objects.get(id=request.GET.get('id_training'))
    try:
        struct_obj = StructureObject.objects.get(id=request.GET.get('_id'))
    except ObjectDoesNotExist:
        struct_obj = None
    try:
        parent = StructureObject.objects.get(id=request.GET.get('id_parent'))
    except ObjectDoesNotExist:
        parent = None
    if not struct_obj:
        return JsonResponse({
            'nature': "",
            'regime': parent.regime if parent else training.MECC_type,
            'session': parent.session if parent else training.session_type,
            'label': "",
            'is_in_use': True,
            'period': parent.period if parent else "",
            'ECTS_credit': "",
            'RESPENS_id': "",
            'external_name': "",
            'mutual': "",
            'ROF_ref': "",
            'ROF_code_year': "",
            'ROF_nature': "",
            'ROF_supply_program': "",
            'ref_si_scol': "",
            'period_fix': True if parent else False,
        })
    try:
        respens = User.objects.get(username=struct_obj.RESPENS_id)
        name_respens = respens.first_name + " " + respens.last_name
    except User.DoesNotExist:
        name_respens = None
    j = {
        'nature': struct_obj.nature,
        'regime': struct_obj.regime,
        'session': struct_obj.session,
        'label': struct_obj.label,
        'is_in_use': struct_obj.is_in_use,
        'period': parent.period if parent else struct_obj.period,
        'ECTS_credit': struct_obj.ECTS_credit,
        'external_name': struct_obj.external_name,
        'RESPENS_id': struct_obj.RESPENS_id,
        'name_respens': name_respens,
        'mutual': struct_obj.mutual,
        'ROF_ref': struct_obj.ROF_ref,
        'ROF_code_year': struct_obj.ROF_code_year,
        'ROF_nature': struct_obj.ROF_nature,
        'ROF_supply_program': struct_obj.ROF_supply_program,
        'ref_si_scol': struct_obj.ref_si_scol,
        'period_fix': True if parent else False,
    }
    if request.user.is_superuser:
        j.update({
            'is_imported': ObjectsLink.objects.get(id_child=struct_obj.id, id_parent=request.GET.get('id_parent')).is_imported,
            'parent_label': parent.label if parent else 'no parent label to display',
            'parent_rof_ref': parent.ROF_ref if parent else 'no ROF reference to display',
        })
    return JsonResponse(j)


def update_respens_label(username, new_label, training, old_label):
    profile = Profile.objects.get(
        code="RESPENS", cmp=training.supply_cmp,
        year=currentyear().code_year, label="RESPENS - %s" % old_label)

    profile.label = "RESPENS - %s" % new_label
    profile.save()


def remove_respens(old_username, label, training):
    """
    Remove respens profile and delete user/meccuser if no
    more profile on it
    """
    try:
        meccuser = MeccUser.objects.get(user__username=old_username)
    except MeccUser.DoesNotExist as e:
        return
    profile = Profile.objects.get(
        code="RESPENS", cmp=training.supply_cmp, year=currentyear().code_year,
        label="RESPENS - %s" % label)
    meccuser.profile.remove(profile)

    if len(meccuser.profile.all()) < 1:
        User.objects.get(username=old_username).delete()
        meccuser.delete()


@login_required
@is_post_request
def remove_imported(request, id):
    """
    remove object link from imported mecc
    """
    link = ObjectsLink.objects.get(id=id)
    currentpage = '/mecctable/training/%s' % link.id_training

    link.delete()
    return redirect(currentpage)


@login_required
@is_post_request
def remove_object(request, id_struct, id_link):
    """
    Remove struct_obj and related object_link
    """
    struc = StructureObject.objects.get(id=id_struct)
    link = ObjectsLink.objects.filter(id_child=id_struct)

    # def get_children(parent, children_list=[]):
    #     """
    #     Return a list of children from a parent
    #     """
    #     for e in ObjectsLink.objects.filter(id_parent=parent.id_child):
    #         children_list.append(e)
    #         get_children(e, children_list)
    #     return children_list
    #
    # for e in get_children(link):
    #     struct = StructureObject.objects.get(id=e.id_child)
    #
    #     remove_respens(struct.RESPENS_id, struct.label, Training.objects.get(
    #         id=struct.owner_training_id))
    #     struct.delete()
    #     e.delete()

    remove_respens(struc.RESPENS_id, struc.label, Training.objects.get(
        id=struc.owner_training_id))
    if link.count() == 1:
        struc.delete()
        link.delete()
    else:
        link.get(id=id_link).delete()

    return redirect('/mecctable/training/' + str(struc.owner_training_id))


@login_required
@is_post_request
@is_ajax_request
def mecctable_update(request):
    """
    Update mecctable
    """
    training = Training.objects.get(id=request.POST.get('training_id'))
    is_catalogue = 'CATALOGUE' in training.degree_type.short_label
    institute = Institute.objects.get(code__exact=training.supply_cmp)

    # needed stuff in order to create objectslink
    id_parent = int(request.POST.get('id_parent'))
    id_child = int(request.POST.get('id_child'))
    data_form = request.POST.get('formdata')
    is_mutual = True if request.POST.get('is_mutual') == 'true' else False
    j = json.loads(data_form)
    data = {}
    username = j.get('RESPENS_id')
    user_data = get_user_from_ldap(username=username) if username not in [
        '', ' ', None] else None

    def create_respens(username):
        """
        Create meccuser/user and RESPENS profile
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(
                last_name=user_data.get("last_name"),
                email=user_data.get('mail'),
                username=username, first_name=user_data.get(
                    'first_name').title())
        profile, created = Profile.objects.get_or_create(
            code="RESPENS", label="RESPENS - %s" % j.get('label'),
            cmp=training.supply_cmp, year=currentyear().code_year)
        try:
            meccuser = MeccUser.objects.get(user__username=username)
        except MeccUser.DoesNotExist:
            meccuser = MeccUser.objects.create(
                user=user, cmp=user_data.get('main_affectation_code'),
                status='PROF')

        meccuser.profile.add(profile)

    def create_new_struct():
        """
        Create structure
        """
        if j.get('RESPENS_id') not in ['', ' ', None]:
            create_respens(j.get('RESPENS_id'))

        return StructureObject.objects.create(
            code_year=currentyear().code_year,
            nature=j.get('nature'),
            owner_training_id=training.id,
            cmp_supply_id=training.supply_cmp,
            regime=j.get('regime') if is_catalogue else training.MECC_type,
            session=j.get(
                'session') if is_catalogue else training.session_type,
            label=j.get('label'),
            is_in_use=True if j.get('is_in_use') else False,
            period=j.get('period'),
            ECTS_credit=None if j.get('ECTS_credit') in [
                0, '', ' '] else j.get('ECTS_credit'),
            RESPENS_id=j.get('RESPENS_id'),
            mutual=is_mutual,
            ROF_ref=j.get('ROF_ref'),
            ROF_code_year=None if j.get('ROF_code_year') in [
                0, '', ' '] else j.get(),
            ROF_nature=j.get('ROF_nature'),
            ROF_supply_program=j.get('ROF_supply_program'),
            ref_si_scol=j.get('ref_si_scol'),
            external_name=j.get('external_name')
        )

    def update_recup_atb_ens(struct):
        """
        Si l'un des quatre champs est modifié, training.recup_atb_ens est mis à True
        cf di/mecc#42
        """
        respens_changed = struct.RESPENS_id != j.get('RESPENS_id') or struct.external_name != j.get('external_name')
        regime_changed = struct.regime != j.get('regime')
        session_changed = struct.session != j.get('session')
        ref_si_scol_changed = struct.ref_si_scol != j.get('ref_si_scol')

        if respens_changed or regime_changed or session_changed or ref_si_scol_changed:
            training.recup_atb_ens = True
            training.save()

    if id_child == 0:
        struct = create_new_struct()
        try:
            coeff = int(struct.ECTS_credit) / int(3)
        except TypeError:
            coeff = None
        try:
            last_order_in_parent = ObjectsLink.objects.filter(
                id_training=training.id,
                id_parent=id_parent, code_year=currentyear().code_year).latest(
                'order_in_child').order_in_child
        except ObjectsLink.DoesNotExist:
            last_order_in_parent = 0
        last_order_in_parent += 1
        try:
            link = ObjectsLink.objects.get(
                id_child=id_child, id_training=training.id,
                id_parent=id_parent, code_year=currentyear().code_year)
        except ObjectsLink.DoesNotExist:
            link = ObjectsLink.objects.create(
                id_child=struct.id,
                code_year=currentyear().code_year,
                id_training=training.id,
                id_parent=id_parent,
                order_in_child=last_order_in_parent,
                coefficient=coeff if struct.nature == 'UE' else None,
                n_train_child=training.n_train,
                # nature_child=j.get('nature')
                nature_child='INT',
                is_imported=False
            )
        if str(training.degree_type.short_label) == 0\
                and int(0 if struct.ECTS_credit is None else struct.ECTS_credit) == 0:
            coeff = 0
        else:
            coeff = coeff if coeff != 0 else None
        link.coefficient = coeff if struct.nature == 'UE' else None
        link.save()
    else:
        struct = StructureObject.objects.get(id=id_child)
        link = ObjectsLink.objects.get(
            id_parent = id_parent,
            id_child = id_child
        )
        # check the respens is the same as before and update respens label
        # if updated
        if struct.label != j.get('label') and struct.RESPENS_id not in ['', ' ', None]:
            update_respens_label(
                struct.RESPENS_id, j.get('label'), training, struct.label)
        if struct.RESPENS_id != j.get('RESPENS_id'):
            if struct.RESPENS_id not in ['', ' ', None]:
                remove_respens(struct.RESPENS_id, j.get('label'), training)
            if j.get('RESPENS_id') not in ['', ' ', None]:
                create_respens(j.get('RESPENS_id'))
        update_recup_atb_ens(struct)
        struct.code_year = currentyear().code_year
        struct.owner_training_id = training.id
        struct.cmp_supply_id = training.supply_cmp
        struct.regime = j.get('regime') if is_catalogue else training.MECC_type
        struct.session = j.get(
            'session') if is_catalogue else training.session_type
        struct.RESPENS_id = j.get('RESPENS_id')
        struct.external_name = j.get('external_name')
        struct.ROF_ref = j.get('ROF_ref')
        struct.ROF_code_year = None if j.get('ROF_code_year') in [
            0, '', ' ', None] else j.get('ROF_code_year')
        struct.ROF_nature = j.get('ROF_nature')
        struct.ROF_supply_program = j.get('ROF_supply_program')
        struct.ref_si_scol = j.get('ref_si_scol')
        if not institute.ROF_support:
            """Champs non modifiables si appui ROF"""
            struct.nature = j.get('nature') if j.get('nature') else struct.nature
            struct.label = j.get('label')
            struct.is_in_use = True if j.get('is_in_use') else False
            struct.ECTS_credit = None if j.get('ECTS_credit') in [
                0, '', ' '] else j.get('ECTS_credit')
            struct.period = j.get('period')
            struct.mutual = is_mutual
        if 'is_imported' in request.POST.keys() and link.is_imported != request.POST.get('is_imported'):
            link.is_imported = True if request.POST.get('is_imported') == 'true' else False

        link.save()
        struct.save()

    return JsonResponse(data)


@login_required
def mecctable_home(request, id=None, template='mecctable/mecctable_home.html'):
    """
    Display mecctable including StructureObject, ObjectsLink and Exam
    """
    code_year = currentyear().code_year
    data = {}
    data['training'] = training = Training.objects.get(id=id)
    supply_cmp = Institute.objects.get(code__exact=training.supply_cmp)
    data['rof_enabled'] = supply_cmp.ROF_support

    current_structures = StructureObject.objects.filter(code_year=code_year)
    current_links = ObjectsLink.objects.filter(code_year=code_year)

    # Si la composante en appui ROF ou la formation est de type Catalogue NS :
    # exclure si is_existing_rof = False
    if supply_cmp.ROF_support or training.degree_type.ROF_code == 'EA':
        current_links = current_links.exclude(
            is_existing_rof=False,
        )

    current_exams = Exam.objects.filter(code_year=code_year)

    root_link = current_links.filter(id_parent='0', id_training=id).order_by(
        'order_in_child').distinct()

    struc_o = set(
        e.cmp_supply_id for e in current_structures.filter(mutual=True))

    data['all_cmp'] = Institute.objects.filter(code__in=struc_o)
    data['next_id'] = current_structures.count() + 1
    data['form'] = StructureObjectForm
    data['notification_to'] = settings.MAIL_FROM
    # user = reques.user.username
    respens_struct = [e.id for e in current_structures.filter(
        RESPENS_id=request.user.username)]

    input_is_open = training.input_opening[0] in ['1', '3']
    user_profiles = request.user.meccuser.profile.all()
    data['la_liste'] = get_mecc_table_order(
        [e for e in root_link], respens_struct, current_structures,
        current_links, current_exams, training, input_is_open, all_exam=False)

    # data['input_is_open'] = input_is_open
    user_is_poweruser = is_poweruser(training, user_profiles, request.user.username)
    data['can_edit'] = (user_is_poweruser and input_is_open) \
                       or request.user.is_superuser \
                       or 'DES1' in [e.name for e in request.user.groups.all()]
    if training.input_opening[0] == "4":
        data['can_edit'] = False

    return render(request, template, data)


@is_post_request
@login_required
def send_mail_respform(request):
    """
    Send mail
    """
    s = "[MECC] Notification"
    b = _("""
    Il s'agit d'un mail de test, Veuillez ne pas le prendre en considération.
    Merci.
    """)
    nobody = ['', ' ', None]
    to = [e.replace(' ', '') for e in request.POST.get('to').split(
        ',')] if request.POST.get('to') not in nobody else None
    cc = [e.replace(' ', '') for e in request.POST.get('cc').split(
        ',')] if request.POST.get('cc') not in nobody else None

    subject = request.POST.get('subject', s) if request.POST.get(
        'subject') not in ['', ' '] else s
    body = request.POST.get('body', b) if request.POST.get(
        'body') not in ['', ' '] else b

    mail = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email="%s %s <%s> " % (
            request.user.first_name,
            request.user.last_name,
            request.user.email),
        to=to,
        cc=cc,
        bcc=[settings.MAIL_ARCHIVES],
    )
    id_training = request.POST.get('id_training')
    mail.send()
    return redirect('/mecctable/training/%s' % id_training)


@login_required
@is_post_request
@is_ajax_request
def update_mecc_position(request):
    """
    Update positions'link object with retrieved data from jquery sortable index
    """
    list_obj = [{
        "id": int(e.split(':')[0]),
        "order": int(e.split(':')[1])} for e in request.POST.get(
        'new_positions').split(',')]

    concerned_obj = ObjectsLink.objects.filter(
        id__in=[a.get('id') for a in list_obj])

    for e in list_obj:
        obj = concerned_obj.get(id=e.get('id'))
        new_order = e.get('order')
        if obj.order_in_child != new_order:
            obj.order_in_child = new_order
            obj.save()

    return JsonResponse({'status': 200})


@login_required
@is_post_request
@is_ajax_request
def reorder_semester(request, training_id):
    """
    Reorder top-level (SE) objects up or down
    :param request:
    :param training_id:
    :return:
    """
    direction = request.POST.get('direction').strip()
    order = int(request.POST.get('order'))

    links = ObjectsLink.objects.filter(
        id_training=training_id,
        id_parent=0,
    ).order_by(
        'order_in_child'
    ).values('order_in_child', 'id')

    if direction == 'down':
        for link in links:
            if link['order_in_child'] == order:
                link['order_in_child'] = order + 1
            elif link['order_in_child'] == order + 1:
                link['order_in_child'] = order
            else:
                pass
    elif direction == 'up':
        for link in links:
            if link['order_in_child'] == order:
                link['order_in_child'] = order - 1
            elif link['order_in_child'] == order - 1:
                link['order_in_child'] = order
            else:
                pass

    for link in links:
        objectslink = ObjectsLink.objects.get(id=link['id'])
        objectslink.order_in_child = link['order_in_child']
        objectslink.save()

    return JsonResponse({'status': 200, })


@is_ajax_request
def copy_old_mecctable2(request):
    """
    Rewrite of copy_old_mecctable otherwise my head will explode
    """
    # GIVE ME ALL YOUR DATAS !!!!!!!!!
    # * YEARS
    current_year = currentyear().code_year
    old_year = current_year - 1
    years = [current_year, old_year]

    # * TRAINING
    trainings = Training.objects.filter(code_year__in=years)
    current_trainings = trainings.filter(code_year=current_year)
    old_trainings = trainings.filter(code_year=old_year)
    training_id = request.GET.get('training_id')
    training = trainings.get(id=training_id)
    old_training = old_trainings.get(n_train=training.n_train)

    # * STRUCTURES
    structures = StructureObject.objects.filter(code_year__in=years)
    current_structures = structures.filter(code_year=current_year)
    old_structures = structures.filter(code_year=old_year)

    # * LINKS
    links = ObjectsLink.objects.filter(code_year__in=years)
    current_links = links.filter(code_year=current_year)
    old_links = links.filter(code_year=old_year)
    old_links_concerned = old_links.filter(id_training=old_training.id)

    mecctable_imported = False

    import copy

    # copy structure function
    def copy_structure(to_copy):
        """
        Return a copy of a structure with brand new stuff
        ACHTUNG : ONLY USEABLE HERE
        """
        new_struct = copy.copy(to_copy)
        if new_struct.RESPENS_id:
            profile, created = Profile.objects.get_or_create(
                code="RESPENS", label="RESPENS - %s" % new_struct.label,
                cmp=training.supply_cmp, year=training.code_year
            )
            meccuser = MeccUser.objects.get(user__username=new_struct.RESPENS_id)
            meccuser.profile.add(profile)
        new_struct.id = None  # Needed to not override exisitng object !
        new_struct.owner_training_id = training.id
        new_struct.regime = training.MECC_type
        new_struct.session = training.session_type
        new_struct.code_year = training.code_year
        new_struct.auto_id = to_copy.auto_id

        new_struct.save()

        return new_struct

    def copy_link(link, new_parent_id, new_child_id):
        """
        Perform a copy of a link with brand new stuff
        ACHTUNG : ONLY USEABLE HERE
        """
        new_link = copy.copy(link)
        new_link.id = None
        new_link.id_training = training.id
        new_link.code_year = training.code_year
        new_link.id_parent = new_parent_id
        new_link.id_child = new_child_id
        new_link.n_train_child = training.n_train if not link.is_imported\
            else current_owner_training.n_train

        new_link.save()

        return new_link

    # ITERATE OVER ALL OLD LINKS CONCERNED
    for ol in old_links_concerned:

        # récuperer les anciennes structures par rapport au lien dans la boucle
        old_struct_child = old_structures.get(id=ol.id_child)
        old_struct_parent = old_structures.get(
            id=ol.id_parent) if ol.id_parent != 0 else None

        # process si la structure n'est pas importée :
        if not ol.is_imported:

            #   - copier la structure fils si elle n'existe pas
            try:
                new_struct_child = current_structures.get(
                    auto_id=old_struct_child.auto_id,
                    owner_training_id=training_id
                )
            except ObjectDoesNotExist:
                new_struct_child = copy_structure(old_struct_child)
            new_child_id = new_struct_child.id

            #   - copier la structure père si elle n'existe pas
            if old_struct_parent:
                try:
                    new_struct_parent = current_structures.get(
                        auto_id=old_struct_parent.auto_id,
                        owner_training_id=training_id
                    )
                except ObjectDoesNotExist:
                    new_struct_parent = copy_structure(old_struct_parent)
                new_parent_id = new_struct_parent.id
            else:
                new_parent_id = 0

            #   - creer un nouveau lien
            try:
                new_link = current_links.get(
                    id_parent=new_parent_id,
                    id_child=new_child_id
                )
            except ObjectDoesNotExist:
                copy_link(
                    link=ol,
                    new_child_id=new_child_id,
                    new_parent_id=new_parent_id
                )

            #   - Si la structure est mutualisée
            if new_struct_child.mutual:
                # MAJ des liens des formations consommatrices de cette structure
                # pour que ces liens pointent vers cette structure
                current_links.filter(
                    id_child=old_struct_child.id
                ).update(
                    id_child=new_child_id
                )

        else:
            # IF OL is imported
            old_owner_training = old_trainings.get(
                id=old_struct_child.owner_training_id
            )
            try:
                current_owner_training = current_trainings.get(
                    n_train=old_owner_training.n_train
                )
                new_struct_child = current_structures.get(
                    auto_id=old_struct_child.auto_id,
                    owner_training_id=current_owner_training.id
                )
            except ObjectDoesNotExist:
                new_struct_child = old_struct_child
                current_owner_training = old_owner_training
            new_child_id = new_struct_child.id

            if old_struct_parent:
                try:
                    new_struct_parent = current_structures.get(
                        auto_id=old_struct_parent.auto_id,
                        owner_training_id=training_id
                    )
                except ObjectDoesNotExist:
                    new_struct_parent = copy_structure(old_struct_parent)
                new_parent_id = new_struct_parent.id
            else:
                new_parent_id = 0

            try:
                new_link = current_links.get(
                    id_parent=new_parent_id,
                    id_child=new_child_id
                )
            except ObjectDoesNotExist:
                new_link = copy_link(
                    link=ol,
                    new_child_id=new_child_id,
                    new_parent_id=new_parent_id
                )

    mecctable_imported = True

    json_response = {"mecctable_imported": mecctable_imported}
    return JsonResponse(json_response)

def copy_old_mecctable(request, id_training):
    """
    Copy year -1 mecctable if exists and :
    •   duplique tous les objets propres de la formation de l’année précédente
        vers la nouvelle année (copie des enregistrements de la table Objets,
        avec ID Année = n-1 et ID de la formation propriétaire = ID de la
        formation courante)
    •   duplique tous les liens entre objets de l’année précédente vers la
        nouvelle année, y compris avec des objets importés (copie des
        enregistrements de la table Architecture_objets, avec ID Année = n-1 et
        ID interne de la formation (contexte) = ID de la formation courante)
            o   les coefficients et les notes seuil des fils au sein des pères
                sont récupérés par ce traitement.
            o   si des objets importés n’existent pas encore dans la nouvelle
                année, ils apparaissent d’abord avec un libellé contenant l’ID
                suivi d’un ? et sans descendance. Leur affichage redevient
                normal dès lors que ces objets sont dupliqués par leur
                propriétaire. Sinon, on peut décider de le décrocher de la
                formation.
    •   Les changements dans les attributs Régime et Session de la formation
        (Onglet Général) doivent être appliqués aux objets propres de la
        structure lors de la duplication ; un message d’information sera
        d’abord affiché.
    """
    # USEFULL DATAS
    training = Training.objects.get(id=id_training)
    old_year = training.code_year - 1
    current_structures = StructureObject.objects.filter(
        code_year=training.code_year)
    current_links = ObjectsLink.objects.filter(code_year=training.code_year)
    old_training = Training.objects.get(
        n_train=training.n_train, code_year=old_year)
    old_structures = StructureObject.objects.filter(code_year=old_year)
    old_links = ObjectsLink.objects.filter(
        code_year=old_year, id_training=old_training.id)

    import copy

    def copy_structure(to_copy):
        """
        Return a copy of a structure with brand new stuff
        ACHTUNG : ONLY USEABLE HERE
        """
        new_struct = copy.copy(to_copy)
        new_struct.id = None  # Needed to not override exisitng object !
        new_struct.owner_training_id = training.id
        new_struct.regime = training.MECC_type
        new_struct.session = training.session_type
        new_struct.code_year = training.code_year
        new_struct.auto_id = to_copy.auto_id
        new_struct.save()
        # take advantage to update_current_links
        update_other_current_links(to_copy, new_struct)

        return new_struct

    def update_other_current_links(old_struct, new_struct):
        """
        Update all current lnks with new created structure => used for create
        auto remove ? on not yet imported structures
        """
        for link in current_links:
            if link.id_child == old_struct.id:
                link.id_child = new_struct.id
                link.save()
                dict_link = link.__dict__
                dict_link.pop('_state', None)
                current_links.update(**dict_link)
            if link.id_parent == old_struct.id:
                link.id_parent = new_struct.id
                link.save()
                dict_link = link.__dict__
                dict_link.pop('_state', None)
                current_links.update(**dict_link)

    for old_link in old_links:
        # 1.0 GET old child structure
        old_struct_child = old_structures.get(id=old_link.id_child)
        # 1.1 Get new child structure
        try:
            new_struct_child = current_structures.get(
                auto_id=old_struct_child.auto_id,
                owner_training_id=old_struct_child.owner_training_id)
        except ObjectDoesNotExist:
            # 1.2 or create it if it belong to this current training
            if old_struct_child.owner_training_id == old_link.id_training:
                new_struct_child = copy_structure(old_struct_child)
            else:
                # else return the old one
                # il faut récuperer l'ancienne structure et verifier
                # qu'elle existe dans les currents sinon on utilise
                # l'ancienne et amen car on va juste mettre un ? =)
                # recuperer la formation qui est liée à l'ancien lien
                old_other_training = Training.objects.get(
                    id=old_struct_child.owner_training_id)
                current_other_training = Training.objects.get(
                    n_train=old_other_training.n_train,
                    code_year=old_year)
                try:
                    new_struct_child = current_structures.get(
                        auto_id=old_struct_child.auto_id,
                        owner_training_id=current_other_training.id)
                except ObjectDoesNotExist:
                    new_struct_child = old_struct_child
        # 2.0 Get old parent structure, beware that it can
        # be root if id_parent == 0

        if old_link.id_parent == 0:
            new_parent_id = 0
        else:
            # 2.1 IF structure parent != root => Get it
            old_struct_parent = old_structures.get(id=old_link.id_parent)
            try:
                new_struct_parent = current_structures.get(
                    auto_id=old_struct_parent.auto_id,
                    owner_training_id=old_struct_parent.owner_training_id)
            except ObjectDoesNotExist:
                # 2.2 or create it
                if old_struct_parent.owner_training_id == old_link.id_training:
                    new_struct_parent = copy_structure(old_struct_parent)
                else:
                    # continue
                    # Specs say that imported structure which doesn't exist
                    # in current year is childless but in order to get further
                    # functionality i'm going to store it anyway (auto update
                    # if old structure is imported)
                    old_other_training = Training.objects.get(
                        id=old_struct_parent.owner_training_id)
                    current_other_training = Training.objects.get(
                        n_train=old_other_training.n_train,
                        code_year=old_year)
                    try:
                        new_struct_parent = current_structures.get(
                            auto_id=old_struct_parent.auto_id,
                            owner_training_id=current_other_training.id)
                    except ObjectDoesNotExist:
                        new_struct_parent = old_struct_parent
            new_parent_id = new_struct_parent.id

        new_child_id = new_struct_child.id

        # 3.0 get new link
        try:
            new_link = current_links.get(
                id_parent=new_parent_id, id_child=new_child_id)
        except ObjectDoesNotExist:
            # 3.1 or create it
            new_link = copy.copy(old_link)
            new_link.id = None
            new_link.id_training = training.id
            new_link.code_year = training.code_year
            new_link.id_parent = new_parent_id
            new_link.id_child = new_child_id
            new_link.n_train_child = training.n_train
            new_link.save()

    return redirect('/mecctable/training/' + str(id_training))

@login_required
def preview_mecctable(request):
    training = request.GET.get('training_id')

    return Document.generate(
        gen_type='pdf',
        model='preview_mecctable',
        trainings=training
    )



# Using generic classview
class StructureObjectListView(ListView):
    model = StructureObject


class StructureObjectCreateView(CreateView):
    model = StructureObject
    form_class = StructureObjectForm


class StructureObjectDetailView(DetailView):
    model = StructureObject


class StructureObjectUpdateView(UpdateView):
    model = StructureObject
    form_class = StructureObjectForm


class ObjectsLinkListView(ListView):
    model = ObjectsLink


class ObjectsLinkCreateView(CreateView):
    model = ObjectsLink
    form_class = ObjectsLinkForm


class ObjectsLinkDetailView(DetailView):
    model = ObjectsLink


class ObjectsLinkUpdateView(UpdateView):
    model = ObjectsLink
    form_class = ObjectsLinkForm


class ExamListView(ListView):
    model = Exam


class ExamCreateView(CreateView):
    model = Exam
    form_class = ExamForm


class ExamDetailView(DetailView):
    model = Exam


class ExamUpdateView(UpdateView):
    model = Exam
    form_class = ExamForm
