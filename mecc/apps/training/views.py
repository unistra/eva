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
        context = super(TrainingListView, self).get_context_data(**kwargs)
        return add_current_year(context)

    @has_requested_cmp
    def get_queryset(self):
        print('here')
        institutes = [e.code for e in Institute.objects.all()]
        if self.kwargs['cmp'] is None:
            return Training.objects.filter(
                code_year=currentyear().code_year).order_by('degree_type')

        if self.kwargs['cmp'] in institutes:
            return Training.objects.all().filter(
                institutes__code=self.kwargs['cmp']).order_by('degree_type')

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
    manage_respform(request.POST.dict())
    return redirect('training:edit', id=t_id)


#
# @is_ajax_request
# @login_required
# def get_list_of_teacher(request):
#     """
#     Ajax : return list of teacher with searched name
#     """
#     data = {}
#     x = request.GET.get('member', '')
#     if len(x) > 1:
#         ppl = [
#             e for e in get_from_ldap(x) if e['username'] not in [
#                 e.username for e in ECICommissionMember.objects.all()
#             ]
#         ]
#         data['pple'] = sorted(ppl, key=lambda x: x['first_name'])
#         return JsonResponse(data)
#     else:
#         return JsonResponse(
#             {'message': _('Veuillez entrer au moins deux caractères.')})
