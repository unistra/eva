"""
Django view for training part
"""
from crispy_forms.templatetags.crispy_forms_filters import as_crispy_field
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django_cas.decorators import login_required

from mecc.apps.files.models import FileUpload
from mecc.apps.institute.models import Institute
from mecc.apps.mecctable.models import StructureObject, ObjectsLink, Exam
from mecc.apps.rules.models import Rule, Paragraph
from mecc.apps.training.forms import SpecificParagraphDerogForm, TrainingForm, \
    AdditionalParagraphForm, ExtraTrainingsForm
from mecc.apps.training.models import Training, SpecificParagraph, \
    AdditionalParagraph
from mecc.apps.training.utils import remove_training, consistency_check, reapply_attributes_previous_year, \
    reapply_respens_and_attributes_from_previous_year
from mecc.apps.utils.documents_generator import Document
from mecc.apps.utils.manage_pple import manage_respform, is_poweruser, \
    is_megauser
from mecc.apps.utils.pdfs import setting_up_pdf, NumberedCanvas, \
    complete_rule, watermark_do_not_distribute
from mecc.apps.utils.queries import currentyear
from mecc.apps.years.models import UniversityYear
from mecc.decorators import is_post_request, is_DES1, has_requested_cmp, \
    is_ajax_request, is_correct_respform


@is_ajax_request
def do_regime_session_check(request):
    """
    Check if the regime or session number of a training has changed
    """
    # DATA
    current_training = Training.objects.get(id=request.GET.get('training_id'))
    old_training = Training.objects.get(
        n_train=current_training.n_train,
        code_year=current_training.code_year-1
    )

    regime_session_changed = True if\
        current_training.MECC_type is not old_training.MECC_type or\
        current_training.session_type is not old_training.session_type\
        else False

    json_response = {
        'regime_session_changed': regime_session_changed,
        'link_clicked': request.GET.get('link_clicked')
    }

    return JsonResponse(json_response)


@is_ajax_request
def do_consistency_check(request):
    """
    call consistency check for a specified training
    """
    training = Training.objects\
        .select_related('degree_type')\
        .get(id=request.GET.get('training_id'))
    report = consistency_check(training)
    to_remove = []

    for e in report:
        if not report.get(e).get('objects'):
            to_remove.append(e)

    for e in to_remove:
        report.pop(e)

    json_response = {"report": report, 'training': training.small_dict}
    return JsonResponse(json_response)


@is_ajax_request
def update_training_regime_session(request):
    """
    ajax call to update session and regime as you want
    """
    # done = save_training_update_regime_session(
    #     Training.objects.get(id=request.POST.get('training_id')),
    #     request.POST.get('regime_type'),
    #     request.POST.get('session_type')
    # )

    done = Training.objects.get(id=request.POST.get('training_id')).transform(
        request.POST.get('mode'),
        request.POST.get('regime_type'),
        request.POST.get('session_type')
    )

    return JsonResponse({'status': 200 if done else 300})

@is_ajax_request
def cancel_transform(request):
    training_form = TrainingForm(
        instance=Training.objects.get(id=request.GET.get('training_id'))
    )
    mecc_type_layout = as_crispy_field(field=training_form['MECC_type'])
    session_type_layout = as_crispy_field(field=training_form['session_type'])

    return JsonResponse({
        'mecc_type_layout': mecc_type_layout,
        'session_type_layout': session_type_layout
    })

def my_teachings(request, template='training/respform_trainings.html'):
    """
    Give owner training of RESPENS
    """
    request.session['visited_cmp'] = 'RESPENS'
    request.session['list_training'] = False
    current_year = currentyear().code_year
    struct_object = StructureObject.objects.filter(
        code_year=current_year, RESPENS_id=request.user.username
    )
    trainings = Training.objects.filter(
        id__in=[e.owner_training_id for e in struct_object]
    ).select_related('degree_type')

    trainings = _filter_out_rof_disabled_trainings(trainings)

    return render(request, template, {
        'trainings': trainings,
    })


@is_ajax_request
@is_post_request
def remove_respform(request):
    """
    AJAX call for removing respform --'
    """
    done = manage_respform({
        "username": request.POST.get('resp_username'),
        "remove": True,
        "formation": request.POST.get('id_training')
    }, request.POST.get('id_training'))
    return JsonResponse({'status': 200 if done else 300})


@is_DES1
@login_required
def list_training(request, template='training/list_cmp.html'):
    """
    View for DES1 - can select CMP
    """
    data = {}
    request.session['list_training'] = True
    data['institutes'] = Institute.objects.all().order_by('field', 'label')
    return render(request, template, data)


@login_required
def list_training_mecc(request, template='training/list_cmp_mecc.html'):
    """
    View for ECI/VP
    """

    current_year = currentyear().code_year
    data = {}
    supply_filter = []

    uy = UniversityYear.objects.get(is_target_year=True)

    institutes = Institute.objects.filter(
        training__code_year=uy.code_year).distinct()

    t = Training.objects.filter(code_year=uy.code_year)

    # get institutes who are supplier for a training
    for training in t:
        if training.supply_cmp in institutes.values_list('code', flat=True):
            supply_filter.append(training.supply_cmp)

    supply_institutes = institutes.filter(
        code__in=supply_filter).distinct().order_by('field', 'label')
    data['institutes'] = supply_institutes
    data['letters'] = FileUpload.objects.filter(object_id__in=data['institutes'].values_list(
        'pk', flat=True), additional_type='letter_%s/%s' % (current_year, current_year + 1))
    files = FileUpload.objects.filter(object_id__in=data['institutes'].values_list(
        'pk', flat=True), additional_type='misc_%s/%s' % (current_year, current_year + 1))
    data['others'] = files.values('object_id').annotate(
        f_count=Count('object_id'))

    return render(request, template, data)


class TrainingListView(ListView):
    """
    Training list view
    """
    model = Training

    def get_context_data(self, **kwargs):
        self.request.session['from_duplicated'] = False
        id_cmp = self.kwargs.get('cmp')
        self.request.session['visited_cmp'] = id_cmp
        self.request.session['list_training'] = False
        context = super(TrainingListView, self).get_context_data(**kwargs)
        context['institute'] = institute = Institute.objects.get(
            code=id_cmp) if id_cmp else "ALL"
        self.request.session['visited_cmp_label'] = context[
            'label_cmp'] = institute.label if id_cmp is not None else "Toutes composantes"
        self.request.session['visited_cmp_id'] = context[
            'code_cmp'] = institute.pk if id_cmp is not None else None
        try:
            context['rof_enabled'] = institute.ROF_support
        except AttributeError:
            context['rof_enabled'] = False

        try:
            context['letter_file'] = FileUpload.objects.filter(
                object_id=context['code_cmp'], additional_type='letter_%s/%s' % (
                    currentyear().code_year, currentyear().code_year + 1))
            context['misc_file'] = FileUpload.objects.filter(
                object_id=context['code_cmp'], additional_type='misc_%s/%s' % (
                    currentyear().code_year, currentyear().code_year + 1))
        except AttributeError:
            """ No year initiliazed !"""
            pass

        return context

    @has_requested_cmp
    def get_queryset(self):
        id_cmp = self.kwargs.get('cmp')
        institute = Institute.objects.get(code=id_cmp) if id_cmp else None
        institutes = [e.code for e in Institute.objects.all()]
        trainings = Training.objects.filter(
            code_year=currentyear().code_year if currentyear() is not None else None
        )
        trainings = trainings.order_by(
            'degree_type', 'label'
        )

        if institute and institute.ROF_support:
            # Si la composante est en appui ROF, ne pas afficher les formations avec is_existing_rof = False
            trainings = trainings.exclude(is_existing_rof=False)
        else:
            # Ne pas afficher la formation si elle est de type catalogue NS et is_existing_rof = False
            trainings = trainings.exclude(is_existing_rof=False, degree_type__ROF_code='EA')

        if id_cmp is None:
            return trainings

        if id_cmp in institutes:
            trainings = trainings.filter(institutes__code=self.kwargs['cmp'])
            return trainings

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
        context['institutes'] = Institute.objects.all().order_by('label')
        context['can_edit'] = True
        context['new'] = True
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
        context['institutes'] = Institute.objects.all().order_by('label')
        context['request.display.current_year'] = "%s/%s" % (
            currentyear().code_year, currentyear().code_year + 1)
        context['resp_form'] = self.object.resp_formations.all()
        context['is_respform'] = True if self.request.user.meccuser in context['resp_form'] else False
        input_is_open = self.object.input_opening[0] in ['1', '3']
        context['can_edit'] = (
            self.request.environ['allowed'] and
            input_is_open
        ) or self.request.user.is_superuser or ('DES1' in [
            e.name for e in self.request.user.groups.all()] and self.object.input_opening[0] != '4')
        context['rof_enabled'] = Institute.objects.get(code=self.object.supply_cmp).ROF_support
        return context


    def post(self, request, *args, **kwargs):
        # En mode ROF les champs Type de diplôme, Intitulé de la formatio,
        # En service et Réf. CP Année ROF sont désactivés (attribut "disabled")
        # Le formulaire ne retourne don aucune valeur pour ces champs
        # Ces champs sont alimentés ici par les infos en base de données
        self.object = self.get_object()  # type: Training
        if Institute.objects.get(code=self.object.supply_cmp).ROF_support:
            request.POST = request.POST.copy()
            request.POST['label'] = self.object.label
            request.POST['degree_type'] = self.object.degree_type.id
            request.POST['is_used'] = self.object.is_used
            request.POST['ref_cpa_rof'] = self.object.ref_cpa_rof
            request.POST['ref_si_scol'] = self.object.ref_si_scol

        return super(TrainingEdit, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        # En mode ROF, si le témoin reappli_atb est positionné à False et que
        # le champ Témoin Tableau MECC est modifié, on
        # positionne le témoin reappli_atb à True (di/mecc#158)
        if self.object.reappli_atb is False:
            if not set(form.changed_data).isdisjoint([
                'MECC_tab',
            ]):
                self.object.reappli_atb = True
        return super(TrainingEdit, self).form_valid(form)

    def form_invalid(self, form):
        return super(TrainingEdit, self).form_invalid(form)


class TrainingDelete(DeleteView):
    """
    Training delete view
    """

    def get_context_data(self, **kwargs):
        context = super(TrainingDelete, self).get_context_data(**kwargs)
        year = self.object.code_year
        can_remove = remove_training(self.request, self.object.id)
        context['message'] = can_remove.get('message')
        context['removable'] = can_remove.get('removable')
        context['confirmed'] = can_remove.get('confirmed')
        rules = [e.n_rule for e in Rule.objects.filter(
            degree_type=self.object.degree_type).filter(
            code_year=self.object.code_year)]
        add_parag = apps.get_model('training', 'AdditionalParagraph')
        spe_parag = apps.get_model('training', 'SpecificParagraph')
        additionals = add_parag.objects.filter(
            training=self.object, code_year=year, rule_gen_id__in=rules)
        specifics = spe_parag.objects.filter(
            training=self.object, code_year=year, rule_gen_id__in=rules)

        context['additionals'] = additionals
        context['specifics'] = specifics
        links = ObjectsLink.objects.filter(id_training=self.object.id)
        context['meccs'] = structs = StructureObject.objects.filter(
            id__in=[link.id_child for link in links])
        context['exams'] = exams = [(e, structs.get(id=e.id_attached)) for e in Exam.objects.filter(
            id_attached__in=[s.id for s in structs])]
        return context

    def get_success_url(self):
        if self.request.session.get('visited_cmp'):
            return reverse('training:list', kwargs={
                'cmp': self.request.session['visited_cmp']})
        return reverse('training:list')

    model = Training
    slug_field = 'id'
    slug_url_kwarg = 'id_training'



@login_required
@is_post_request
def process_respform(request):
    """
    Usefull to handle respfrom
    """
    t_id = request.POST.dict().get('formation')
    manage_respform(request.POST.dict(), t_id)
    return redirect('training:edit', id=t_id)


@login_required
def respform_list(request, template='training/respform_trainings.html'):
    """
    View for respform list all binded training
    """
    request.session['visited_cmp'] = 'RESPFORM'
    request.session['list_training'] = False
    trainings = Training.objects.filter(
        resp_formations=request.user.meccuser,
        code_year=currentyear().code_year if currentyear() is not None else None,
    ).select_related('degree_type')

    trainings = _filter_out_rof_disabled_trainings(trainings)

    return render(request, template, {
        'trainings': trainings,
    })


@login_required
def duplicate_home(request, year=None, template='training/duplicate.html'):
    """
    View for duplicate training from other year to current year
    """
    data = {}
    data['cmp'] = cmp = request.session['visited_cmp']

    current_year = currentyear()
    request.session['from_duplicated'] = True
    data['current_year'] = "%s/%s" % (current_year.code_year,
                                      current_year.code_year + 1)
    trains = Training.objects.all()
    trainings = (trains.filter(
        institutes=Institute.objects.get(code=cmp)).order_by('label')
        if cmp is not None else trains).order_by('label')
    data['availables_years'] = sorted({(e.code_year, "%s/%s" % (
        e.code_year, e.code_year + 1)) for e in trainings}, reverse=True)
    data['existing_trainings'] = existing = trainings.filter(
        code_year=current_year.code_year).order_by('label')
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
    """
    Correct respform can edit rule
    """

    data = {}
    recovered = request.session.pop('recovered', False)
    if recovered:
        data['rec'] = "Le traitement de récupération globale des spécificités \
de l'année précédente est terminé.<br><u>NB</u> : sans écrasement des \
spécificités déjà saisies pour la nouvelle année."
    data['training'] = training = Training.objects.get(id=id)
    rules = Rule.objects.filter(degree_type=training.degree_type).filter(
        code_year=currentyear().code_year, is_in_use=True)
    data['rules_list'] = rules.filter(is_eci=True) if training.MECC_type \
        in 'E' else rules.filter(is_ccct=True)
    data['custom'] = [a.rule_gen_id for a in [
        e for e in SpecificParagraph.objects.filter(
            code_year=currentyear().code_year, training=training)]
    ] + [e.rule_gen_id for e in AdditionalParagraph.objects.filter(
        training=training, code_year=currentyear().code_year)]
    data['notification_to'] = settings.MAIL_FROM
    if hasattr(settings, 'EMAIL_TEST'):
        data['test_mail'] = _("""
Il s'agit d'un mail de test, veuillez ne pas le prendre en considération.
Merci.
        """)
    input_is_open = training.input_opening[0] in ['1', '3']
    data['can_edit'] = (is_poweruser(training,
                                     request.user.meccuser.profile.all(),
                                     request.user.username) \
                        and input_is_open) \
                        or request.user.is_superuser \
                        or 'DES1' in [e.name for e in request.user.groups.all()]
    if training.input_opening[0] == '4':
        data['can_edit'] = False
    return render(request, template, data)


def recover_everything(request, training_id):
    old_year = currentyear().code_year - 1
    training = Training.objects.get(id=training_id)
    rules = Rule.objects.filter(degree_type=training.degree_type).filter(
        code_year=currentyear().code_year, is_in_use=True)
    paragraph_from_rules = Paragraph.objects.filter(rule__in=rules)
    # old_paragraphs = Paragraph.objects.filter(
    #     id__in=[e.origin_parag for e in paragraph_from_rules])
    old_rules = Rule.objects.filter(code_year=old_year, n_rule__in=[
                                    e.n_rule for e in rules])
    try:
        old_training = Training.objects.get(
            n_train=training.n_train, code_year=old_year)
    except Training.DoesNotExist:
        return HttpResponseRedirect(reverse('training:edit_rules',
                                            args=(training_id,)))

    # Recover old additional paragraph if there isn't during current year
    current_additional = AdditionalParagraph.objects.filter(
        code_year=currentyear().code_year,
        training=training)
    rules_with_additional = [e.rule_gen_id for e in current_additional]
    old_additional = AdditionalParagraph.objects.filter(
        code_year=old_year,
        training=old_training)
    for e in old_additional:
        try:
            old_rule = old_rules.get(id=e.rule_gen_id)
            new_rule = rules.filter(n_rule=old_rule.n_rule).first()
        except Rule.DoesNotExist:
            new_rule = None
        if new_rule and new_rule.id not in rules_with_additional:
            r_add, created = AdditionalParagraph.objects.get_or_create(
                code_year=currentyear().code_year,
                training=training,
                rule_gen_id=new_rule.id,
                text_additional_paragraph=e.text_additional_paragraph,
                origin_id=e.id
            )

    # Recover old specific paragraph if there isn't during current year
    for e in rules:
        try:
            old_rule = old_rules.get(n_rule=e.n_rule)
        except Rule.DoesNotExist:
            continue

        if e.has_parag_with_derog and old_rule.has_parag_with_derog:
            old_sp = SpecificParagraph.objects.filter(
                rule_gen_id=old_rule.id, code_year=old_year,
                training_id=old_training.id)
            for s in old_sp:
                current_paragraph = paragraph_from_rules.filter(
                    origin_parag=s.paragraph_gen_id).first()
                if current_paragraph:
                    sp, created = SpecificParagraph.objects.get_or_create(
                        code_year=currentyear().code_year,
                        training=training,
                        rule_gen_id=e.id,
                        paragraph_gen_id=current_paragraph.id,
                        origin_id=s.id
                    )
                    if created:
                        sp.type_paragraph = s.type_paragraph
                        sp.text_specific_paragraph = s.text_specific_paragraph
                        sp.text_motiv = s.text_motiv
                        sp.save()
    request.session['recovered'] = True

    return HttpResponseRedirect(reverse('training:edit_rules',
                                        args=(training_id,)))


@login_required
@is_post_request
def delete_specific(request):
    val = request.POST.get('id')
    if request.POST.get('type') == 'D':
        to_del = SpecificParagraph.objects.get(id=val)
    elif request.POST.get('type') == 'A':
        to_del = AdditionalParagraph.objects.get(id=val)
    else:
        raise Exception('Not a correct type')
        # pass
    to_del.delete()
    return HttpResponseRedirect(request.environ.get('HTTP_REFERER'))


@is_ajax_request
def ask_delete_specific(request):
    if request.GET.get('type') in 'A':
        p = AdditionalParagraph.objects.get(id=request.GET.get('val'))
        text = p.text_additional_paragraph
    elif request.GET.get('type') in 'D':
        p = SpecificParagraph.objects.get(id=request.GET.get('val'))
        text = p.text_specific_paragraph
    else:
        raise Exception("%s is not a correct value" % request.GET.get('type'))

    json_response = {
        'text': text,
        'title': str(p),
        'id': p.id
    }
    return JsonResponse(json_response)


@is_correct_respform
def specific_paragraph(request, training_id, rule_id, template="training/specific_paragraph.html"):
    data = {}
    data['url_to_del'] = "/training/delete_specific/"
    data['training'] = t = Training.objects.get(id=training_id)
    data['rule'] = r = Rule.objects.get(id=rule_id)
    data['parag'] = p = Paragraph.objects.filter(rule=data['rule'])
    data['specific_paragraph'] = SpecificParagraph.objects.filter(
        code_year=currentyear().code_year, training=t, rule_gen_id=r.id)
    try:
        data['additional_paragraph'] = AdditionalParagraph.objects.get(
            code_year=currentyear().code_year, training=t, rule_gen_id=r.id)
    except AdditionalParagraph.DoesNotExist:
        data['additional_paragraph'] = None

    # GET OLD STUFF
    old_year = currentyear().code_year - 1
    old_training = Training.objects.filter(
        n_train=t.n_train, code_year=old_year).first()
    can_be_recup = True if r.is_edited == 'N' else False

    if old_training:
        old_specific = SpecificParagraph.objects.filter(
            code_year=old_year).filter(paragraph_gen_id__in=[
                e.origin_parag for e in p
            ], training_id=old_training.id) if old_training else []
        try:
            old_additional = AdditionalParagraph.objects.filter(
                code_year=currentyear().code_year - 1,
                rule_gen_id=Rule.objects.get(code_year=old_year, n_rule=r.n_rule).id,
                training_id=old_training.id
            )
        except (AdditionalParagraph.DoesNotExist, Rule.DoesNotExist):
            old_additional = None

        data['old_specific'] = [
            e.paragraph_gen_id for e in old_specific] if can_be_recup else False

    else:
        old_additional = None

    # PROCESSING WITH DATAS
    data['old_additional'] = True if old_additional and can_be_recup else False
    data['specific_ids'] = [
        a.paragraph_gen_id for a in data['specific_paragraph']]
    return render(request, template, data)


def gen_pdf_all_rules(request, training_id):

    training = Training.objects.get(id=training_id)
    year = training.code_year
    r = Rule.objects.filter(
        degree_type=training.degree_type,
        is_in_use=True,
        code_year=year)
    rules = r.filter(is_eci=True) if training.MECC_type \
        in 'E' else r.filter(is_ccct=True)
    sp = SpecificParagraph.objects.filter(
        code_year=year, training=training,  rule_gen_id__in=[e.id for e in rules])
    ap = AdditionalParagraph.objects.filter(
        training=training, code_year=year)
    # PDF gen
    title = training.label
    response, doc = setting_up_pdf(title, margin=42)
    story = complete_rule(year, title, training, rules, sp, ap)

    doc.build(
        story, onFirstPage=watermark_do_not_distribute,
        onLaterPages=watermark_do_not_distribute, canvasmaker=NumberedCanvas)
    return response


def edit_additional_paragraph(request, training_id, rule_id, n_rule, old="N", template="training/form/edit_specific_paragraph.html"):
    data = {}
# CURRENT OBJECTS
    training = data['training'] = Training.objects.get(id=training_id)
    data['title'] = _("Alinéa additionnel")
    rule = data['rule'] = Rule.objects.get(id=rule_id)
    data['from_id'] = rule_id
    input_is_open = training.input_opening[0] in ['1', '3']
    data['can_apply_to_others'] = ((
        is_megauser(training, request.user.meccuser.profile.all()) and input_is_open) \
        or 'DES1' in [e.name for e in request.user.groups.all()] \
        or request.user.is_superuser)

    # OLD STUFF
    old_year = currentyear().code_year - 1
    old_training = Training.objects.get(
        code_year=old_year, n_train=training.n_train) if old == 'Y' else None
    old_rule = Rule.objects.get(
        code_year=old_year, n_rule=n_rule) if old == 'Y' else None
    old_additional = AdditionalParagraph.objects.get(
        code_year=old_year, rule_gen_id=old_rule.id, training_id=old_training.id) if old == 'Y' else None

# Create temporary additional; just in order to fill the form with ease
    additional, created = AdditionalParagraph.objects.get_or_create(
        code_year=currentyear().code_year,
        rule_gen_id=rule.id,
        training=training,
    ) if old != "Y" else AdditionalParagraph.objects.get_or_create(
        code_year=currentyear().code_year,
        rule_gen_id=rule.id,
        training=training,
        text_additional_paragraph=old_additional.text_additional_paragraph,
        origin_id=old_additional.id
    )

    data['add_form'] = AdditionalParagraphForm(
        instance=additional,
        prefix='add'
    )
    data['extra_trainings_form'] = ExtraTrainingsForm(
        training=training,
        rule=rule,
        additional=additional,
        prefix="ext"
    )
# Delete temporary additional paragraph if created
    if created:
        additional.origin_id = additional.id + 1
        additional.save()
        additional.delete()

    data['additional'] = _("Vous souhaitez ajouter un alinéa à cette règle pour \
votre formation. Merci de la rédiger ci-dessous :")
    if request.method == 'POST':
        add_form = AdditionalParagraphForm(
            request.POST,
            instance=additional,
            prefix='add'
        )
        if data['can_apply_to_others']:
            extra_trainings_form = ExtraTrainingsForm(
                data=request.POST,
                training=training,
                rule=rule,
                additional=additional,
                prefix="ext"
            )
        if add_form.is_valid():
            add_form.save()
            try:
                extra_trainings_form
            except:
                pass
            else:
                if extra_trainings_form.is_valid():
                    for training_id in extra_trainings_form.cleaned_data['extra_trainings']:
                        add, created = AdditionalParagraph.objects.\
                            update_or_create(
                                defaults=add_form.cleaned_data,
                                training=Training.objects.get(id=training_id),
                                code_year=additional.code_year,
                                rule_gen_id=additional.rule_gen_id,
                                origin_id=additional.origin_id
                            )
            return redirect(
                'training:specific_paragraph',
                training_id=training_id, rule_id=rule_id)

    return render(request, template, data)


@is_correct_respform
def edit_specific_paragraph(request, training_id, rule_id, paragraph_id, n_rule, old='N', template="training/form/edit_specific_paragraph.html"):
    data = {}
    # CURRENT OBJECTS
    data['title'] = _("Dérogation")
    data['from_id'] = rule_id
    data['training'] = training = Training.objects.get(id=training_id)
    data['paragraph'] = p = Paragraph.objects.get(id=paragraph_id)
    data['text_derog'] = p.text_derog
    data['text_motiv'] = p.text_motiv
    data['rule'] = r = Rule.objects.get(id=rule_id)
    input_is_open = training.input_opening[0] in ['1', '3']
    data['can_apply_to_others'] = ((
        is_megauser(training, request.user.meccuser.profile.all()) and input_is_open) \
        or 'DES1' in [e.name for e in request.user.groups.all()] \
        or request.user.is_superuser) # \
        # and SpecificParagraph.objects.filter(
        #     code_year=currentyear().code_year,
        #     paragraph_gen_id=paragraph_id,
        #     training_id=training_id
        # ).count() > 0

    # OLD OBJECTS
    old_year = currentyear().code_year - 1 if old == "Y" else None
    old_rule = Rule.objects.filter(
        n_rule=n_rule, code_year=old_year).first() if old == "Y" else None
    try:
        old_training = Training.objects.get(
            code_year=old_year, n_train=training.n_train) if old_rule else None
    except Training.DoesNotExist:
        old_training = None
    try:
        old_sp = SpecificParagraph.objects.get(
            code_year=old_year,
            rule_gen_id=old_rule.id,
            training=old_training,
            paragraph_gen_id=p.origin_parag) if old_rule else None
    except SpecificParagraph.DoesNotExist:
        old_sp = None

    sp, created = SpecificParagraph.objects.get_or_create(
        code_year=currentyear().code_year,
        training=training,
        rule_gen_id=r.id,
        paragraph_gen_id=paragraph_id,
    )

    if created:
        sp.text_specific_paragraph = p.text_standard if old_sp is None \
            else old_sp.text_specific_paragraph
        sp.text_motiv = "" if old_sp is None else old_sp.text_motiv
        sp.origin_id = old_sp.id if old_sp else sp.id
        sp.save()

    data['specific_form'] = SpecificParagraphDerogForm(
        instance=sp,
        prefix="spe"
    )
    data['extra_trainings_form'] = ExtraTrainingsForm(
        training=training,
        rule=r,
        specific=sp,
        prefix="ext"
    )

    if created:
        sp.delete()

    if request.method == 'POST':
        specific_form = SpecificParagraphDerogForm(
            data=request.POST,
            instance=sp,
            prefix="spe"
        )
        if data['can_apply_to_others']:
            extra_trainings_form = ExtraTrainingsForm(
                data=request.POST,
                training=training,
                rule=r,
                specific=sp,
                prefix="ext"
            )
        if specific_form.is_valid():
            specific_form.save()
            try:
                extra_trainings_form
            except:
                pass
            else:
                if extra_trainings_form.is_valid():
                    for training_id in extra_trainings_form.cleaned_data['extra_trainings']:
                        specific, created = SpecificParagraph.objects.\
                            update_or_create(
                                defaults=specific_form.cleaned_data,
                                training=Training.objects.get(id=training_id),
                                code_year=sp.code_year,
                                rule_gen_id=sp.rule_gen_id,
                                paragraph_gen_id=sp.paragraph_gen_id,
                                origin_id=sp.origin_id
                            )
            return redirect(
                'training:specific_paragraph',
                training_id=training.id, rule_id=rule_id)
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
            # date_val_cmp=t.date_val_cmp,
            # date_res_des=t.date_res_des,
            # date_visa_des=t.date_visa_des,
            # date_val_cfvu=t.date_val_cfvu,
            supply_cmp=t.supply_cmp,
            n_train=t.n_train,
            reappli_atb=False,
            recup_atb_ens=False,
        )
        for cmp in t.institutes.all():
            training.institutes.add(cmp)
        for y in t.resp_formations.all():
            dic = {}
            t_id = dic['formation'] = training.id
            dic['username'] = y.user.username
            dic['mail'] = y.user.email
            dic['name'] = y.user.last_name
            dic['firstname'] = y.user.first_name
            dic['cmp'] = y.cmp
            dic['add_respform'] = "Oui"
            manage_respform(dic, t_id)

        labels.append(training.label)
        n_trains.append(training.n_train)
    return JsonResponse(
        {'status': 'added', 'n_trains': n_trains, 'labels': labels})


@is_post_request
@login_required
def send_mail(request):
    """
    Send notification mail to des-admin-mecc@unistra.fr
    """

    cc = request.POST.get('cc').split(',') if request.POST.get('cc') else ''
    subject = request.POST.get('subject')
    body = request.POST.get('body')
    mail = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email="%s %s <%s> " % (
            request.user.first_name, request.user.last_name,
            request.user.email),
        to=[settings.MAIL_FROM],
        cc=cc,
    )
    mail.send()
    messages.success(request, _('Notification envoyée.'))
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def preview_mecc(request):

    return Document.generate(
        gen_type='pdf',
        model='preview_mecc',
        trainings=request.GET.get('training_id')
    )


def _filter_out_rof_disabled_trainings(trainings):
    # ne pas garder les formations supprimées dans ROF
    filtered_trainings = []
    institutes_with_rof_support = Institute.objects.filter(
        ROF_support=True
    ).values_list(
        'code', flat=True
    )
    for training in trainings:
        if training.supply_cmp in institutes_with_rof_support:
            # ne pas garder si is_existing_rof = False
            if training.is_existing_rof:
                filtered_trainings.append(training)
        else:
            # ne pas garder si type Catalogue NS et is_existing_rof = False
            if not(training.degree_type.ROF_code == 'EA' and training.is_existing_rof is False):
                filtered_trainings.append(training)

    return filtered_trainings


@login_required
@is_ajax_request
@is_post_request
def reapply_atb(request):
    year = currentyear()
    institute = get_object_or_404(Institute, code=request.POST.get('institute'), ROF_support=True)
    processed_trainings, skipped_trainings = reapply_attributes_previous_year(institute, year)
    processed = [t.label for t in processed_trainings]
    skipped = [t.label for t in skipped_trainings]
    return JsonResponse({'skipped': skipped, 'processed': processed})


@login_required
@is_ajax_request
@is_post_request
def recup_atb_ens(request):
    training = get_object_or_404(Training, pk=request.POST.get('training'))
    processed, message = reapply_respens_and_attributes_from_previous_year(training)
    return JsonResponse({'processed': processed, 'message': message})
