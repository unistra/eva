from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Training
from .forms import TrainingForm
from mecc.apps.utils.querries import currentyear
from mecc.apps.institute.models import Institute
from django.core.urlresolvers import reverse
from django_cas.decorators import login_required

from mecc.decorators import is_post_request, is_DES1, has_requested_cmp
from mecc.apps.utils.manage_pple import manage_respform
from django.shortcuts import render, redirect


def add_current_year(dic):
    dic['disp_current_year'] = "%s/%s" % (
        currentyear().code_year, currentyear().code_year + 1)
    return dic


@is_DES1
@login_required
def list_training(request, template='training/list_cmp.html'):
    """
    View for DES1 - can select CMP
    """
    data = {}
    data['institutes'] = Institute.objects.all().order_by('field', 'label')
    add_current_year(data)
    return render(request, template, data)


class TrainingListView(ListView):
    """
    Training list view
    """
    model = Training

    def get_context_data(self, **kwargs):
        id_cmp = self.kwargs.get('cmp')
        print(self.kwargs)
        context = super(TrainingListView, self).get_context_data(**kwargs)
        context['label_cmp'] = Institute.objects.get(
            code=id_cmp).label if id_cmp is not None else "Toutes composantes"
        self.request.session['visited_cmp'] = self.kwargs.get('cmp')
        return add_current_year(context)

    @has_requested_cmp
    def get_queryset(self):
        institutes = [e.code for e in Institute.objects.all()]
        trainings = Training.objects.filter(
            code_year=currentyear().code_year).order_by('degree_type')
        if self.kwargs['cmp'] is None:
            return trainings

        if self.kwargs['cmp'] in institutes:
            return trainings.filter(institutes__code=self.kwargs['cmp'])

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
        context['institutes'] = Institute.objects.all()
        return add_current_year(context)

    def get_success_url(self):
        return reverse('training:edit', args=(self.object.id,))


class TrainingEdit(UpdateView):
    """
    Training update view
    """
    model = Training
    form_class = TrainingForm
    pk_url_kwarg = 'id'

    def get_success_url(self):
        if self.request.method == 'POST' and 'new_training' \
           in self.request.POST:
            return reverse('training:new')
        elif self.request.method == 'POST' and 'stay' in self.request.POST:
            return reverse('training:edit', kwargs={'id': self.object.id})
        else:
            return reverse('training:list')

    def get_context_data(self, **kwargs):
        context = super(TrainingEdit, self).get_context_data(**kwargs)
        context['institutes'] = Institute.objects.all()

        context['disp_current_year'] = "%s/%s" % (
            currentyear().code_year, currentyear().code_year + 1)
        context['object'] = self.object
        context['resp_form'] = self.object.resp_formations.all()
        # context['validation_form'] = ValidationTrainingForm(
        #     instance=self.object)
        return context


class TrainingDelete(DeleteView):
    def get_context_data(self, **kwargs):
        context = super(TrainingDelete, self).get_context_data(**kwargs)
        return add_current_year(context)

    # def get_success_url(self):

    model = Training
    slug_field = 'id'
    slug_url_kwarg = 'id_training'
    success_url = '/training/list'


@login_required
@is_post_request
def process_respform(request):
    t_id = request.POST.dict().get('formation')

    manage_respform(request.POST.dict(), t_id)
    return redirect('training:edit', id=t_id)
