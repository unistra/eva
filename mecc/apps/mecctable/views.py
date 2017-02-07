from django.views.generic import DetailView, ListView, UpdateView, CreateView
from .models import StructureObject, ObjectsLink, Exam
from .forms import StructureObjectForm, ObjectsLinkForm, ExamForm
from django.shortcuts import render, redirect
from mecc.apps.training.models import Training


def mecctable_home(request, id=None, template='mecctable/mecctable_home.html'):
    """
    View displaying mecctable including StructureObject, ObjectsLink and
    Exam - sort of all-in-one -
    """
    # structure = StructureObject.objects.filter
    data = {}
    training = Training.objects.get(id=id)
    data['training'] = training
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
