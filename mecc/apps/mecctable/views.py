from django.views.generic import DetailView, ListView, UpdateView, CreateView
from .models import StructureObject, ObjectsLink, Exam
from .forms import StructureObjectForm, ObjectsLinkForm, ExamForm
from django.shortcuts import render, redirect
from mecc.apps.institute.models import Institute
from mecc.apps.training.models import Training
from django.http import JsonResponse
from mecc.apps.utils.queries import currentyear
from mecc.apps.utils.ws import get_user_from_ldap
from mecc.decorators import is_post_request, is_ajax_request
from django_cas.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
import json
from django.contrib.auth.models import User
from mecc.apps.adm.models import MeccUser, Profile
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from decimal import InvalidOperation


@is_ajax_request
@is_post_request
def update_grade_coeff(request):
    """
    ajax view to update grade and coeff
    """
    val = strip_tags(request.POST.get('value'))
    to_update = request.POST.get('to_update')
    type_to_update = to_update.split('-')[-1]
    id_to_update = to_update.split('-')[0]
    link = ObjectsLink.objects.get(id=id_to_update)
    if type_to_update == "coeff":
        old_coeff = link.coefficient
        try:
            link.coefficient = float(val.replace(",", "."))
            link.save()
            value = link.coefficient
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
            if int(val) < 0:
                return JsonResponse({
                    "status": 'ERROR',
                    "val": old_grade,
                    "error": _("Veuillez entrer un nombre positif")
                })
            link.eliminatory_grade = int(val)
            link.save()
            value = link.eliminatory_grade
        except ValueError:
            if val in ['', ' ']:
                link.eliminatory_grade = None
                link.save()
                return JsonResponse({"status": 'OK', "val": val})
            return JsonResponse({
                "status": 'ERROR',
                "val": old_grade,
                "error": _("Veuillez entrer un nombre entier")
            })
    return JsonResponse({"status": 'OK', "val": value})


@is_ajax_request
def get_stuct_obj_details(request):
    """
    Get details of structure, if it DoesNotExist return empty fields
    """
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
            'regime': "",
            'session': "",
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
        'mutual': struct_obj.mutual,
        'ROF_ref': struct_obj.ROF_ref,
        'ROF_code_year': struct_obj.ROF_code_year,
        'ROF_nature': struct_obj.ROF_nature,
        'ROF_supply_program': struct_obj.ROF_supply_program,
        'ref_si_scol': struct_obj.ref_si_scol,
        'period_fix': True if parent else False
    }
    return JsonResponse(j)


def remove_respens(old_username, label, training):
    """
    Remove respens profile and delete user/meccuser if no
    more profile on it
    """
    try:
        meccuser = MeccUser.objects.get(user__username=old_username)
    except MeccUser.DoesNotExist:
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
def remove_object(request, id):
    """
    Remove struct_obj and relating object_link
    """
    struc = StructureObject.objects.get(id=id)
    link = ObjectsLink.objects.get(id_child=id)

    def get_children(parent, children_list=[]):
        """
        Return a list of children from a parent
        """
        for e in ObjectsLink.objects.filter(id_parent=parent.id_child):
            children_list.append(e)
            get_children(e, children_list)
        return children_list

    for e in get_children(link):

        struct = StructureObject.objects.get(id=e.id_child)

        remove_respens(struct.RESPENS_id, struct.label, Training.objects.get(
            id=struct.owner_training_id))
        struct.delete()
        e.delete()

    remove_respens(struc.RESPENS_id, struc.label, Training.objects.get(
        id=struc.owner_training_id))
    struc.delete()
    link.delete()

    return redirect('/mecctable/training/' + str(struc.owner_training_id))


@is_post_request
@is_ajax_request
def mecctable_update(request):
    """
    Update mecctable
    """

    training = Training.objects.get(id=request.POST.get('training_id'))
    is_catalgue = 'CATALOGUE' in training.degree_type.short_label

    # needed stuff in order to create objectslink
    id_parent = int(request.POST.get('id_parent'))
    id_child = int(request.POST.get('id_child'))
    b = request.POST.get('formdata')
    j = json.loads(b)
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
            last_name = "%s (%s)" % (user_data.get("last_name"), user_data.get(
                'birth_name')) if user_data.get('last_name').capitalize(
                    ) != user_data.get('birth_name').capitalize(
                        ) else user_data.get('last_name')
            user = User.objects.create_user(
                last_name=last_name, email=user_data.get('mail'),
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
            regime=j.get('regime') if is_catalgue else training.MECC_type,
            session=j.get('session') if is_catalgue else training.session_type,
            label=j.get('label'),
            is_in_use=True if j.get('is_in_use') else False,
            period=j.get('period'),
            ECTS_credit=None if j.get('ECTS_credit') in [
                0, '', ' '] else j.get('ECTS_credit'),
            RESPENS_id=j.get('RESPENS_id'),
            mutual=True if j.get('mutual') else False,
            ROF_ref=j.get('ROF_ref'),
            ROF_code_year=None if j.get('ROF_code_year') in [
                0, '', ' '] else j.get(),
            ROF_nature=j.get('ROF_nature'),
            ROF_supply_program=j.get('ROF_supply_program'),
            ref_si_scol=j.get('ref_si_scol'),
            external_name=j.get('external_name')
        )

    if id_child == 0:
        struct = create_new_struct()
    else:
        struct = StructureObject.objects.get(id=id_child)
        # check the respens is the same as before
        if struct.RESPENS_id != j.get('RESPENS_id'):
            if struct.RESPENS_id not in ['', ' ', None]:
                remove_respens(struct.RESPENS_id,  j.get('label'), training)
            if j.get('RESPENS_id') not in ['', ' ', None]:
                create_respens(j.get('RESPENS_id'))
        struct.code_year = currentyear().code_year
        struct.nature = j.get('nature')
        struct.owner_training_id = training.id
        struct.cmp_supply_id = training.supply_cmp
        struct.regime = j.get('regime') if is_catalgue else training.MECC_type
        struct.session = j.get(
            'session') if is_catalgue else training.session_type
        struct.label = j.get('label')
        struct.is_in_use = True if j.get('is_in_use') else False
        struct.period = j.get('period')
        struct.ECTS_credit = None if j.get('ECTS_credit') in [
            0, '', ' '] else j.get('ECTS_credit')
        struct.RESPENS_id = j.get('RESPENS_id')
        struct.external_name = j.get('external_name')
        struct.mutual = True if j.get('mutual') else False
        struct.ROF_ref = j.get('ROF_ref')
        struct.ROF_code_year = None if j.get('ROF_code_year') in [
            0, '', ' '] else j.get()
        struct.ROF_nature = j.get('ROF_nature')
        struct.ROF_supply_program = j.get('ROF_supply_program')
        struct.ref_si_scol = j.get('ref_si_scol')
        struct.save()
    try:
        coeff = int(struct.ECTS_credit)/int(3)
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
        link = ObjectsLink.objects.get(id_child=struct.id)
    except ObjectsLink.DoesNotExist:
        link = ObjectsLink.objects.create(
            id_child=struct.id, code_year=currentyear().code_year,
            id_training=training.id, id_parent=id_parent,
            order_in_child=last_order_in_parent,
            coefficient=coeff if struct.nature == 'UE' else None,
            n_train_child=training.n_train, nature_child=j.get('nature')
        )

    if 'DU' in str(training.degree_type.short_label) and coeff == 0:
        coeff = 0
    else:
        coeff = coeff if coeff != 0 else None
    link.coefficient = coeff if struct.nature == 'UE' else None
    link.save()
    return JsonResponse(data)


def mecctable_home(request, id=None, template='mecctable/mecctable_home.html'):
    """
    View displaying mecctable including StructureObject, ObjectsLink and Exam
    """

    def sort_list(object_list):
        for p in object_list:
            if p.id_parent in [0, '', None]:
                tmp.append(p)
            else:
                parent = ObjectsLink.objects.get(id_child=p.id_parent).id_child
                parent_list.append(p.id_parent)
                current_child = [e.id_parent for e in tmp].count(p.id_parent)
                index = [e.id_child for e in tmp].index(parent) + 1
                tmp.insert(index+current_child, p)
        return tmp

    data = {}
    all_cmp = Institute.objects.all()
    training = Training.objects.get(id=id)
    structure_obj = StructureObject.objects.filter(
        code_year=currentyear().code_year)
    object_link = ObjectsLink.objects.filter(
        code_year=currentyear().code_year,
        id_training=id).order_by('id_parent', 'order_in_child')
    data['next_id'] = StructureObject.objects.count() + 1
    data['training'] = training
    data['all_cmp'] = all_cmp
    data['structure_objs'] = structure_obj
    tmp = []
    parent_list = []
    data['object_link'] = sort_list(object_link)
    data['form'] = StructureObjectForm
    data['parents'] = parent_list
    return render(request, template, data)


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
