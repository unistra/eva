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

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import logging

logger = logging.getLogger(__name__)


@login_required
def import_objectslink(request):
    """
    Create objectslink with selected structureobject
    """
    try:
        id_training = request.POST.get('id_training')
        id_parent = request.POST.get('asking_id')
        cy = currentyear().code_year
        selected_id = map(int, request.POST.getlist('selected_id[]'))
        object_link_list = [
            ObjectsLink.objects.get(
                id=e, code_year=cy) for e in selected_id
        ]
        for e in object_link_list:
            order_in_child = ObjectsLink.objects.filter(
                code_year=cy, id_parent=id_parent).count() + 1
            a, b = ObjectsLink.objects.get_or_create(
                code_year=cy,
                id_training=id_training,
                id_parent=id_parent,
                id_child=e.id,
                order_in_child=order_in_child,
                n_train_child=e.n_train_child,
                nature_child=e.nature_child,
                is_imported=True
            )
    except Exception as e:
        logger.error('CANNOT IMPORT ObjectsLink : \n{error}'.format(error=e))

        return JsonResponse({"error": e})
    return JsonResponse({
        "status": 200,
    })


@is_ajax_request
def get_consom(request):
    """
    Give consomateur of a certain imported object
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
        'year': "%s/%s" % (so.code_year, so.code_year+1),
        'structure': {
            'label': so.label,
            'nature': so.nature,
            'si_scol': so.ref_si_scol,
            'rof': so.ROF_ref},
        'trainings': t if len(t) > 0 else 0,
        'status': 200})


@login_required
@is_ajax_request
def get_mutual_by_cmp(request):
    """
    Give list of suggested cmp according by
    """
    try:
        asking = StructureObject.objects.get(
            id=request.GET.get('asking_id')) if request.GET.get(
                'asking_id') is not '0' else None
        asking_period = asking.period if asking else None
        training_id = request.GET.get('training_id')
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
            cmp_supply_id=request.GET.get('cmp_code'), mutual=True,
            is_in_use=True).exclude(nature__in=to_exclude).exclude(
                owner_training_id=int(training_id))
        if asking_period:
            s_list = s_list.filter(period=asking_period)
        mutual_list = [[
            "<input name='suggest-id' value='%s' type='checkbox'>" % (e.id),
            e.nature,
            Training.objects.get(id=e.owner_training_id).label,
            e.label,
            e.get_regime_display(),
            e.get_session_display(),
            e.ECTS_credit,
            e.external_name if e.external_name else e.get_respens_name,
            e.ref_si_scol,
            e.ROF_ref
        ] for e in s_list]
        data['suggest'] = mutual_list
    except Exception as e:
        print(e)
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
    if type_to_update == "coeff":
        old_coeff = link.coefficient
        if "nbsp" in val or val in ['', ' ', '&nbsp;', '&nbsp;&nbsp;']:
            link.eliminatory_grade = None
            link.save()
            return JsonResponse({"status": 'OK', "val": ""})
        try:
            link.coefficient = float(val.replace(",", "."))
            link.save()
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
            value = link.eliminatory_grade
        except ValueError:
            if "nbsp" in val or val in ['', ' ', '&nbsp;', '&nbsp;&nbsp;']:
                link.eliminatory_grade = None
                link.save()
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
        name_respens = respens.last_name + " " + respens.first_name
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


@login_required
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
            regime=j.get('regime') if is_catalgue else training.MECC_type,
            session=j.get('session') if is_catalgue else training.session_type,
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
        struct.mutual = is_mutual
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
        link = ObjectsLink.objects.get(
            id_child=id_child, id_training=training.id,
            id_parent=id_parent, code_year=currentyear().code_year)
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


@login_required
def mecctable_home(request, id=None, template='mecctable/mecctable_home.html'):
    """
    Display mecctable including StructureObject, ObjectsLink and Exam
    """
    data = {}
    code_year = currentyear().code_year

    current_structures = StructureObject.objects.filter(code_year=code_year)
    current_links = ObjectsLink.objects.filter(code_year=code_year)

    root_link = current_links.filter(id_parent='0', id_training=id).order_by(
        'order_in_child').distinct()

    so = [e.cmp_supply_id for e in current_structures.filter(mutual=True)]
    data['all_cmp'] = Institute.objects.filter(code__in=so)
    data['training'] = Training.objects.get(id=id)
    data['next_id'] = current_structures.count() + 1
    data['form'] = StructureObjectForm

    def recurse(link):
        links = not isinstance(link, (list, tuple)) and [link] or link
        stuff = []

        def get_childs(link, is_imported, rank=0):
            rank += 1
            structure = current_structures.get(id=link.id_child)
            children = current_links.filter(
                id_parent=link.id_child).order_by('order_in_child')
            imported = True if link.is_imported or is_imported else False
            items = {
                "link": link,
                'structure': structure,
                'is_imported': imported,
                'has_childs': True if len(children) > 0 else False,
                'children': [get_childs(
                    e, imported, rank=rank) for e in children],
                'rank': rank - 1,
                'loop': range(0, rank-1),
            }
            return items
        for link in links:
            imported = True if link.is_imported else False
            stuff.append(get_childs(link, imported))

        return stuff

    data['la_liste'] = recurse([e for e in root_link])
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
    # TODO: A decommenter pour envoyer aux bonnes personnes
    # nobody = ['', ' ', None]
    # to = [e.replace(' ', '') for e in request.POST.get('to').split(
    #     ',')] if request.POST.get('to') not in nobody else None
    # cc = [e.replace(' ', '') for e in request.POST.get('cc').split(
    #     ',')] if request.POST.get('cc') not in nobody else None
    # TODO: remove the following lines in production
    to = [
        'weible@unistra.fr'
        ]
    cc = ['ibis.ismail@unistra.fr']

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
