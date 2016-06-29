from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Training
from .forms import TrainingForm, ValidationTrainingForm, InstituteTrainingForm
from mecc.apps.utils.querries import currentyear
from mecc.apps.institute.models import Institute
from mecc.apps.adm.models import Profile
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect


def add_current_year(context):
    context['disp_current_year'] = "%s/%s" % (
        currentyear().code_year, currentyear().code_year + 1)
    return context


class TrainingListView(ListView):
    """
    Training list view
    """
    model = Training

    def get_context_data(self, **kwargs):
        context = super(TrainingListView, self).get_context_data(**kwargs)
        return add_current_year(context)

    def get_queryset(self):
        institutes = [e.code for e in Institute.objects.all()]
        user_profiles = [
                e.code for e in self.requerequest.POSTst.user.meccuser.profile.all()
            ] if self.request.user.is_superuser is not True else [
                e.code for e in Profile.objects.all()
            ]

        if self.kwargs['cmp'] in institutes:
            # TODO: filtrer les formations en fonction des compostantes
            cmp = self.kwargs['cmp']
            return Training.objects.all().order_by('degree_type')

        else:
            return Training.objects.all().order_by('degree_type')

    template_name = 'training/training_list.html'


class TrainingCreate(CreateView):
    """
    Training year create view
    """
    model = Training
    success_url = '/training/list'
    form_class = TrainingForm

    def get_context_data(self, **kwargs):
        context = super(TrainingCreate, self).get_context_data(**kwargs)
        context['disp_current_year'] = "%s/%s" % (
            currentyear().code_year, currentyear().code_year + 1)
        return context

    def get_success_url(self):
        return reverse('training:edit', args=(self.object.id,))


def edit_training(request, id, template='training/training_form.html'):
    """
    Edit training
    """
    data = {}
    training = Training.objects.get(id=id)
    if request.method == 'POST':
        form = TrainingForm(request.POST)
        if form.is_valid():
            train = form.save(commit=False)
            train.save()
        itf = InstituteTrainingForm(request.POST)
        if itf.is_valid():
            print('hello')
            train = form.save(commit=False)
            train = form.save()
    else:
        form = TrainingForm(instance=training)
        itf = InstituteTrainingForm(instance=training)
    data['form'] = form
    data['itf'] = itf
    data['object'] = training
    return render(request, template, data)


class TrainingDelete(DeleteView):
    def get_context_data(self, **kwargs):
        context = super(TrainingDelete, self).get_context_data(**kwargs)
        return add_current_year(context)

    # def get_success_url(self):

    model = Training
    slug_field = 'id'
    slug_url_kwarg = 'id_training'
    success_url = '/training/list'
