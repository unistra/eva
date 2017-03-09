from django.views.generic import DetailView, ListView, UpdateView, CreateView
from .models import StructureObject, ObjectsLink, Exam
from .forms import StructureObjectForm, ObjectsLinkForm, ExamForm
from django.shortcuts import render, redirect
from mecc.apps.training.models import Training
from django.http import JsonResponse
from mecc.apps.utils.querries import currentyear
from mecc.decorators import is_post_request, is_ajax_request
from django_cas.decorators import login_required
import json


@is_ajax_request
def get_stuct_obj_details(request):
    if request.GET.get('_id') in ['', 0, '0', None]:
        return JsonResponse({
            'nature': "",
            'regime': "",
            'session': "",
            'label': "",
            'is_in_use': True,
            'period': "",
            'ECTS_credit': "",
            'RESPENS_id': "",
            'mutual': "",
            'ROF_ref': "",
            'ROF_code_year': "",
            'ROF_nature': "",
            'ROF_supply_program': "",
            'ref_si_scol': ""
        })
    struct_obj = StructureObject.objects.get(id=request.GET.get('_id'))
    j = {
        'nature': struct_obj.nature,
        'regime': struct_obj.regime,
        'session': struct_obj.session,
        'label': struct_obj.label,
        'is_in_use': struct_obj.is_in_use,
        'period': struct_obj.period,
        'ECTS_credit': struct_obj.ECTS_credit,
        'RESPENS_id': struct_obj.RESPENS_id,
        'mutual': struct_obj.mutual,
        'ROF_ref': struct_obj.ROF_ref,
        'ROF_code_year': struct_obj.ROF_code_year,
        'ROF_nature': struct_obj.ROF_nature,
        'ROF_supply_program': struct_obj.ROF_supply_program,
        'ref_si_scol': struct_obj.ref_si_scol
    }
    return JsonResponse(j)


@login_required
@is_post_request
def remove_object(request, id):
    """
    Remove struct_obj and relating object_link
    """
    struct_obj = StructureObject.objects.get(id=id)
    obj_link = ObjectsLink.objects.get(id_child=id)

    if True:
        obj_link.delete()
        struct_obj.delete()
    return redirect('/mecctable/training/' + str(struct_obj.owner_training_id))


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

    def create_new_struct():
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
        )


    try:
        structure = StructureObject.objects.get(id=id_child)
        structure.label = j.get('label')
        structure.save()
        print(structure.label)
        print(structure.id)
        print(id_child)
    except StructureObject.DoesNotExist as e:
        print('GOTu')
        print(e)
        structure = create_new_struct()

    print(structure.label)
    print('DONE')
    #
    #
    # try:
    #     print(id_child)
    #     if id_child is not 0:
    #         struct = StructureObject.objects.get(id=id_child).update(
    #             code_year=currentyear().code_year,
    #             nature=j.get('nature'),
    #             owner_training_id=training.id,
    #             cmp_supply_id=training.supply_cmp,
    #             regime=j.get('regime') if is_catalgue else training.MECC_type,
    #             session=j.get('session') if is_catalgue else training.session_type,
    #             label=j.get('label'),
    #             is_in_use=True if j.get('is_in_use') else False,
    #             period=j.get('period'),
    #             ECTS_credit=None if j.get('ECTS_credit') in [
    #                 0, '', ' '] else j.get('ECTS_credit'),
    #             RESPENS_id=j.get('RESPENS_id'),
    #             mutual=True if j.get('mutual') else False,
    #             ROF_ref=j.get('ROF_ref'),
    #             ROF_code_year=None if j.get('ROF_code_year') in [
    #                 0, '', ' '] else j.get(),
    #             ROF_nature=j.get('ROF_nature'),
    #             ROF_supply_program=j.get('ROF_supply_program'),
    #             ref_si_scol=j.get('ref_si_scol'),
    #         )
    #         print('la')
    #     else:
    #         struct = create_new_struct()
    # except Exception as e:
    #     struct = create_new_struct()
    # # struct.code_year = currentyear().code_year
    # # struct.nature = j.get('nature')
    # # struct.owner_training_id = training.id
    # # struct.cmp_supply_id = training.supply_cmp
    # # struct.regime = j.get('regime') if is_catalgue else training.MECC_type
    # # struct.session = j.get('session') if is_catalgue else training.session_type
    # # print(struct.label)
    # # struct.label = j.get('label')
    # # struct.save()
    # # print(struct.label)
    # # print(j.get('label'))
    # # struct.is_in_use = True if j.get('is_in_use') else False
    # # struct.period = j.get('period')
    # # struct.ECTS_credit = None if j.get('ECTS_credit') in [
    # #     0, '', ' '] else j.get('ECTS_credit')
    # # struct.RESPENS_id = j.get('RESPENS_id')
    # # struct.mutual = True if j.get('mutual') else False
    # # struct.ROF_ref = j.get('ROF_ref')
    # # struct.ROF_code_year = None if j.get('ROF_code_year') in [
    # #     0, '', ' '] else j.get()
    # # struct.ROF_nature = j.get('ROF_nature')
    # # struct.ROF_supply_program = j.get('ROF_supply_program')
    # # struct.ref_si_scol = j.get('ref_si_scol')
    # # print(struct.id)
    # # print([e.label for e in StructureObject.objects.all()])
    # # struct.save()
    # try:
    #     print('$$$$$^^')
    #     print(struct.nature)
    # except Exception as e:
    #     print(e)
    # try:
    #     last_order_in_parent = ObjectsLink.objects.filter(
    #         id_training=training.id,
    #         id_parent=id_parent, code_year=currentyear().code_year).latest(
    #             'order_in_child').order_in_child
    # except ObjectsLink.DoesNotExist:
    #     last_order_in_parent = 0
    # last_order_in_parent += 1
    # try:
    #     ObjectsLink.objects.get(id_child=struct.id)
    # except Exception as e:
    #
    #     ObjectsLink.objects.create(
    #         id_child=struct.id, code_year=currentyear().code_year,
    #         id_training=training.id, id_parent=id_parent,
    #         order_in_child=last_order_in_parent,
    #         n_train_child=training.n_train
    #     )

    return JsonResponse(data)


def mecctable_home(request, id=None, template='mecctable/mecctable_home.html'):
    """
    View displaying mecctable including StructureObject, ObjectsLink and
    Exam - sort of all-in-one -
    """
    data = {}
    training = Training.objects.get(id=id)
    structure_obj = StructureObject.objects.filter(
        code_year=currentyear().code_year,
        owner_training_id=id)
    object_link = ObjectsLink.objects.filter(
        code_year=currentyear().code_year,
        id_training=id)
    data['next_id'] = StructureObject.objects.count() + 1
    data['training'] = training
    data['structure_objs'] = structure_obj
    data['object_link'] = object_link.order_by('id_parent', 'order_in_child')
    data['form'] = StructureObjectForm
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
