from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Training
from .forms import TrainingForm, ValidationTrainingForm
from mecc.apps.utils.querries import currentyear
from mecc.apps.institute.models import Institute
from mecc.apps.adm.models import Profile
from django.core.urlresolvers import reverse
from django_cas.decorators import login_required


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
                e.code for e in self.request.user.meccuser.profile.all()
            ] if self.request.user.is_superuser is not True else [
                e.code for e in Profile.objects.all()
            ]

        print(user_profiles)
        print('-4sqd564sq563d15qs63d1--*/-dqs5dqs')
        print(self.kwargs['cmp'])
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
        print(self.object.resp_formations.all())
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
