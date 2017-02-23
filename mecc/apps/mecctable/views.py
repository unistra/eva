from django.views.generic import DetailView, ListView, UpdateView, CreateView
from .models import StructureObject, ObjectsLink, Exam
from .forms import StructureObjectForm, ObjectsLinkForm, ExamForm
from django.shortcuts import render, redirect
from mecc.apps.training.models import Training
from django.http import JsonResponse
from mecc.apps.utils.querries import currentyear


def mecctable_update(request):
    """
    Update mecctable
    """
    import json  # cannot be outside ?
    if request.is_ajax() and request.method == 'POST':

        training = Training.objects.get(id=request.POST.get('training_id'))
        # needed stuff in order to create objectslink
        id_parent = request.POST.get('id_parent')
        id_child = request.POST.get('id_child')
        ##################################
        b = request.POST.get('formdata')
        j = json.loads(b)
        json = {}

        structure_object = StructureObject.objects.get_or_create(
            code_year=currentyear().code_year,
            nature=j.get('nature'),
            owner_training_id=training.id,
            cmp_supply_id=training.supply_cmp,
            regime=j.get('regime'),
            session=j.get('session'),
            label=j.get('label'),
            is_in_use=True if j.get('is_in_use') == 'on' else False,
            period=j.get('period'),
            ECTS_credit=j.get('ECTS_credit'),
            RESPENS_id=j.get('RESPENS_id'),
            mutual=True if j.get('mutual') == 'on' else False,
            ROF_ref=j.get('ROF_ref'),
            ROF_code_year=j.get('ROF_code_year'),
            ROF_nature=j.get('ROF_nature'),
            ROF_supply_program=j.get('ROF_supply_program'),
            ref_si_scol=j.get('ref_si_scol'),
        )

        print(StructureObject.objects.all().first())
        return JsonResponse(json)


def mecctable_home(request, id=None, template='mecctable/mecctable_home.html'):
    """
    View displaying mecctable including StructureObject, ObjectsLink and
    Exam - sort of all-in-one -
    """
    # structure = StructureObject.objects.filter
    data = {}
    training = Training.objects.get(id=id)
    structure_obj = StructureObject.objects.filter(owner_training_id=id)
    data['next_id'] = StructureObject.objects.count() + 1
    data['training'] = training
    data['structure_objs'] = structure_obj
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
