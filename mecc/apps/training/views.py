from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Training
from .forms import TrainingForm
from mecc.apps.utils.querries import currentyear
from mecc.apps.institute.models import Institute
from django.core.urlresolvers import reverse
from django_cas.decorators import login_required
from mecc.apps.rules.models import Rule
from mecc.decorators import is_post_request, is_DES1, has_requested_cmp, \
    is_ajax_request
from mecc.apps.utils.manage_pple import manage_respform
from django.shortcuts import render, redirect
from django.db import transaction
from django.http import JsonResponse


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


@login_required
def respform_list(request, template='training/respform_trainings.html'):
    """
    View for respform list all binded training
    """
    data = {}
    data['trainings'] = Training.objects.filter(
        resp_formations=request.user.meccuser).filter(
        code_year=currentyear().code_year)
    return render(request, template, data)


@login_required
def duplicate_home(request, year=None, template='training/duplicate.html'):
    """
    View for duplicate training from other year to current year
    """
    data = {}
    current_year = currentyear()
    data['current_year'] = "%s/%s" % (current_year.code_year,
                                      current_year.code_year + 1)

    all_trainings = Training.objects.all()

    data['availables_years'] = sorted({(e.code_year, "%s/%s" % (
        e.code_year, e.code_year + 1)) for e in all_trainings}, reverse=True)
    data['existing_trainings'] = current = all_trainings.filter(
        code_year=current_year.code_year)
    data['asked_year'] = None if year is None else int(year)

    if year is None:
        return render(request, template, data)
    else:
        data['trainings'] = all_trainings.filter(code_year=year)
    return render(request, template, data)


def edit_rules(request, id, template="training/edit_rules.html"):
    data = {}
    data['training'] = training = Training.objects.get(id=id)
    data['rules_list'] = Rule.objects.filter(degree_type=training.degree_type)
    print(data['rules_list'])
    return render(request, template, data)


@transaction.atomic
@login_required
@is_ajax_request
@is_post_request
def duplicate_add(request):
    x = request.POST.getlist('list_id[]')
    list_train = []
    for e in x:
        try:
            x = Training.objects.get(id=e)
            list_train.append(x)
        except Exception:
            pass

    pass


def duplicate_remove(request):
    pass
#
# def duplicaaate_add(request):
#     current_year = currentyear()
#     x = request.POST.getlist('list_id[]')
#
#     dic = [{'year': e.split('_')[0], 'n_rule': e.split('_')[-1]} for e in x]
#     labels = []
#     for e in dic:
#
#         r = Rule.objects.filter(
#             code_year=e.get('year')).filter(n_rule=e.get('n_rule')).first()
#         rule = Rule.objects.create(
#             display_order=r.display_order,
#             code_year=current_year.code_year,
#             label=r.label,
#             is_in_use=r.is_in_use,
#             is_edited='N',
#             is_eci=r.is_eci,
#             is_ccct=r.is_ccct,
#             n_rule=r.n_rule
#         )
#         for a in r.degree_type.all():
#             degree_type = DegreeType.objects.get(id=a.id)
#             rule.degree_type.add(degree_type)
#         rule.save()
#
#         paragraphs = Paragraph.objects.filter(
#             code_year=e.get('year')).filter(rule__id=r.id)
#
#         for p in paragraphs:
#             p.rule.add(rule)
#             p.save()
#
#         labels.append(r.label)
#     return JsonResponse({'status': 'added', 'n_rule': [
#         e.get('n_rule') for e in dic], 'labels': labels})
#
#
# @login_required
# @is_ajax_request
# @is_post_request
# def duplicaaaate_remove(request):
#     x = request.POST.get('id')
#     rule = Rule.objects.get(id=x)
#     label = rule.label
#     # paragraphs = Paragraph.objects.filter(rule__id=x)
#     # Correct test will be later
#     # for p in paragraphs:
#     #     if p.is_cmp or p.is_interaction:
#     #         return JsonResponse({
#     #             "error": "%s comporte des dérogations." % (label)})
#
#     rule.delete()
#
#     return JsonResponse({"status": "removed", "label": label})