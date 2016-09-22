from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Training, SpecificParagraph
from mecc.apps.adm.models import Profile
from .forms import TrainingForm
from mecc.apps.utils.querries import currentyear
from mecc.apps.institute.models import Institute
from django.core.urlresolvers import reverse
from django_cas.decorators import login_required
from mecc.apps.rules.models import Rule, Paragraph
from mecc.decorators import is_post_request, is_DES1, has_requested_cmp, \
    is_ajax_request, is_correct_respform
from mecc.apps.utils.manage_pple import manage_respform
from django.shortcuts import render, redirect
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from .forms import SpecificParagraphCmpForm, SpecificParagraphDerogForm


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
        self.request.session['visited_cmp'] = id_cmp
        context = super(TrainingListView, self).get_context_data(**kwargs)
        self.request.session['visited_cmp_label'] = context['label_cmp'] = Institute.objects.get(
            code=id_cmp).label if id_cmp is not None else "Toutes composantes"
        self.request.session['visited_cmp_id'] = Institute.objects.get(
            code=id_cmp).pk if id_cmp is not None else None
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
        context['institutes'] = Institute.objects.all().order_by('label')
        context['disp_current_year'] = "%s/%s" % (
            currentyear().code_year, currentyear().code_year + 1)
        context['object'] = self.object
        context['resp_form'] = self.object.resp_formations.all()
        # user_profile = request.user.meccuser.profile.all()
        expected_profile = Profile.objects.filter(
            cmp=self.object.supply_cmp,
            year=currentyear().code_year,
            code="RESPFORM")

        context['can_edit'] = (self.request.environ['allowed']
                               or self.request.user.is_superuser)
        # (True if expected_profile
        #                        in self.request.user.meccuser.profile.all()
        #                        or self.request.user.is_superuser
        #                        else False)

        return context


class TrainingDelete(DeleteView):

    def get_context_data(self, **kwargs):
        context = super(TrainingDelete, self).get_context_data(**kwargs)
        return add_current_year(context)

    def get_success_url(self):
        if self.request.session['visited_cmp']:
            return reverse('training:list', kwargs={
                'cmp': self.request.session['visited_cmp']})
        return reverse('training:list')

    model = Training
    slug_field = 'id'
    slug_url_kwarg = 'id_training'


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
    request.session['visited_cmp'] = 'RESPFORM'
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
    cmp = request.session['visited_cmp']
    data = {}
    current_year = currentyear()
    data['current_year'] = "%s/%s" % (current_year.code_year,
                                      current_year.code_year + 1)

    trainings = Training.objects.all().filter(
        institutes=Institute.objects.get(code=cmp
    )) if cmp is not None else Training.objects.all()
    data['availables_years'] = sorted({(e.code_year, "%s/%s" % (
        e.code_year, e.code_year + 1)) for e in trainings}, reverse=True)
    data['existing_trainings'] = existing = trainings.filter(
        code_year=current_year.code_year)
    data['asked_year'] = None if year is None else int(year)

    if year is None:
        return render(request, template, data)
    else:
        data['trainings'] = [
            e for e in trainings.filter(code_year=year) if e.label not in [
                a.label for a in existing]]
    return render(request, template, data)


@is_correct_respform
def edit_rules(request, id, template="training/edit_rules.html"):
    data = {}
    data['training'] = training = Training.objects.get(id=id)
    rules = Rule.objects.filter(degree_type=training.degree_type).filter(
        code_year=currentyear().code_year)
    data['rules_list'] = rules.filter(is_eci=True) if training.MECC_type in 'E' \
        else rules.filter(is_ccct=True)
    return render(request, template, data)


def specific_paragraph(request, training_id, rule_id, template="training/specific_paragraph.html"):

    data = {}
    data['training'] = Training.objects.get(id=training_id)
    data['rule'] = rule = Rule.objects.get(id=rule_id)
    data['parag'] = Paragraph.objects.filter(rule=data['rule'])

    return render(request, template, data)


def edit_specific_paragraph(request, training_id, rule_id, paragraph_id, template="training/form/edit_specific_paragraph.html"):
    data = {}

    data['training'] = t = Training.objects.get(id=training_id)
    data['rule'] = r = Rule.objects.get(id=rule_id)
    data['paragraph'] = p = Paragraph.objects.get(id=paragraph_id)
    data['title'] = _('Alinéa de composante') if p.is_cmp is True else _('Dérogation')

    sp, created = SpecificParagraph.objects.get_or_create(
        code_year=currentyear().code_year,
        training=t,
        rule_gen_id=r.id,
        paragraph_gen_id=p.id,
        type_paragraph="C" if p.is_cmp else "D",
    )
    data['form'] = (SpecificParagraphCmpForm(instance=sp) if p.is_cmp
                    else SpecificParagraphDerogForm(instance=sp))

    data['text_derog'] = p.text_derog
    data['text_motiv'] = p.text_motiv


    if request.method == 'POST':
        form = (SpecificParagraphCmpForm(request.POST, instance=sp)
                if p.is_cmp else SpecificParagraphDerogForm(request.POST,
                instance=sp))
        if form.is_valid():
            form.save()
            return redirect(
                'training:specific_paragraph', training_id=t.id, rule_id=r.id)

    return render(request, template, data)


@is_post_request
@is_ajax_request
def update_progress_rule_statut(request):
    training = Training.objects.get(pk=request.POST.get('id'))
    training.progress_rule = request.POST.get('progress')
    training.save()
    return JsonResponse({
        'status': 'updated', 'progress': training.get_progress_rule_display()})


@transaction.atomic
@login_required
@is_ajax_request
@is_post_request
def duplicate_add(request):
    x = request.POST.getlist('list_id[]')
    labels = []
    n_trains = []
    for e in x:
        t = Training.objects.get(pk=e)
        training = Training.objects.create(
            code_year=currentyear().code_year,
            degree_type=t.degree_type,
            label=t.label,
            is_used=t.is_used,
            MECC_type=t.MECC_type,
            session_type=t.session_type,
            ref_cpa_rof=t.ref_cpa_rof,
            ref_si_scol=t.ref_si_scol,
            date_val_cmp=t.date_val_cmp,
            date_res_des=t.date_res_des,
            date_visa_des=t.date_visa_des,
            date_val_cfvu=t.date_val_cfvu,
            supply_cmp=t.supply_cmp,
            n_train=t.n_train
        )
        for cmp in t.institutes.all():
            training.institutes.add(cmp)
        for y in t.resp_formations.all():
            training.resp_formations.add(y)

        labels.append(training.label)
        n_trains.append(training.n_train)
    return JsonResponse(
        {'status': 'added', 'n_trains': n_trains, 'labels': labels})


def duplicate_remove(request):
    x = request.POST.get('id')
    t = Training.objects.get(pk=x)
    label = t.label
    for y in t.resp_formations.all():
        for profile in y.profile.all():
            if profile.code in 'RESPFORM' and \
                currentyear().code_year == profile.year and profile.cmp in \
                    [e.code for e in t.institutes.all()]:
                    y.profile.remove(profile)
                    t.resp_formations.remove(y)
                    if len(y.profile.all()) < 1:
                        user = User.objects.get(meccuser=y)
                        user.delete()
                        y.delete()
    t.delete()
    return JsonResponse({"status": "removed", "label": label})
