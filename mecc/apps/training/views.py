"""
Django view for training part
"""

from mecc.apps.utils.queries import currentyear
from mecc.apps.institute.models import Institute
from mecc.apps.rules.models import Rule, Paragraph
from mecc.decorators import is_post_request, is_DES1, has_requested_cmp, \
    is_ajax_request, is_correct_respform
from mecc.apps.utils.manage_pple import manage_respform
from mecc.apps.utils.pdfs import setting_up_pdf, NumberedCanvas, \
    complete_rule, watermark_do_not_distribute
from mecc.apps.files.models import FileUpload
from mecc.apps.mecctable.models import StructureObject, ObjectsLink
from mecc.apps.training.models import Training, SpecificParagraph, AdditionalParagraph
from mecc.apps.training.forms import SpecificParagraphDerogForm, TrainingForm, \
    AdditionalParagraphForm
from mecc.apps.training.utils import remove_training

from django_cas.decorators import login_required
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.apps import apps


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

        self.request.session['visited_cmp_label'] = context['label_cmp'] = Institute.objects.get(
            code=id_cmp).label if id_cmp is not None else "Toutes composantes"
        self.request.session['visited_cmp_id'] = context['code_cmp'] = Institute.objects.get(
            code=id_cmp).pk if id_cmp is not None else None

        context['letter_file'] = FileUpload.objects.filter(
            object_id=context['code_cmp'], additional_type='letter_%s/%s' % (
                currentyear().code_year, currentyear().code_year + 1))
        context['misc_file'] = FileUpload.objects.filter(
            object_id=context['code_cmp'], additional_type='misc_%s/%s' % (
                currentyear().code_year, currentyear().code_year + 1))

        return context

    @has_requested_cmp
    def get_queryset(self):
        institutes = [e.code for e in Institute.objects.all()]
        trainings = Training.objects.filter(
            code_year=currentyear().code_year
            if currentyear() is not None else None).order_by('degree_type')

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
        context['institutes'] = Institute.objects.all().order_by('label')
        context['can_edit'] = True
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
        input_is_open = self.object.input_opening[0] in ['1', '3']
        context['can_edit'] = (
            self.request.environ['allowed'] and
            input_is_open
        ) or self.request.user.is_superuser or 'DES1' in [
            e.name for e in self.request.user.groups.all()]
        if not input_is_open:
            context['can_edit'] = False
        
        return context


class TrainingDelete(DeleteView):
    """
    Training delete view
    """

    def get_context_data(self, **kwargs):
        context = super(TrainingDelete, self).get_context_data(**kwargs)
        current_year = currentyear().code_year
        can_remove = remove_training(self.request, self.object.id)
        context['message'] = can_remove.get('message')
        context['removable'] = can_remove.get('removable')
        add_parag = apps.get_model('training', 'AdditionalParagraph')
        spe_parag = apps.get_model('training', 'SpecificParagraph')
        additionals = add_parag.objects.filter(
            training=self.object, code_year=current_year)
        specifics = spe_parag.objects.filter(
            training=self.object, code_year=current_year)
        context['additionals'] = additionals
        context['specifics'] = specifics
        links = ObjectsLink.objects.filter(id_training=self.object.id)
        context['meccs'] = StructureObject.objects.filter(
            id__in=[link.id_child for link in links])
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

    data = {}
    data['trainings'] = Training.objects.filter(
        resp_formations=request.user.meccuser).filter(
            code_year=currentyear().code_year if currentyear() is not None else None)
    return render(request, template, data)


@login_required
def duplicate_home(request, year=None, template='training/duplicate.html'):
    """
    View for duplicate training from other year to current year
    """
    cmp = request.session['visited_cmp']
    data = {}
    current_year = currentyear()
    request.session['from_duplicated'] = True
    data['current_year'] = "%s/%s" % (current_year.code_year,
                                      current_year.code_year + 1)

    trainings = (Training.objects.all().filter(
        institutes=Institute.objects.get(code=cmp)).order_by('label')
        if cmp is not None else Training.objects.all()).order_by('label')
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
    data['rules_list'] = rules_list = rules.filter(is_eci=True) if training.MECC_type \
        in 'E' else rules.filter(is_ccct=True)
    # for aa in rules_list:
    #     print(aa.__dict__)
    data['custom'] = [a for a in [
        e.rule_gen_id for e in SpecificParagraph.objects.filter(
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

    data['can_edit'] = (request.environ['allowed'] and input_is_open) or request.user.is_superuser or 'DES1' in [
        e.name for e in request.user.groups.all()]
    if training.input_opening[0] in ['4', '2']:
        data['can_edit'] = False
    return render(request, template, data)


def recover_everything(request, training_id):
    training = Training.objects.get(id=training_id)
    rules = Rule.objects.filter(degree_type=training.degree_type).filter(
        code_year=currentyear().code_year, is_in_use=True)
    old_year = currentyear().code_year - 1
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
    old_additional = AdditionalParagraph.objects.filter(
        code_year=old_year,
        training=old_training)
    for e in old_additional:
        if e.rule_gen_id not in [c.rule_gen_id for c in current_additional]:
            r_add, created = AdditionalParagraph.objects.get_or_create(
                code_year=currentyear().code_year,
                training=training,
                rule_gen_id=e.rule_gen_id,
                text_additional_paragraph=e.text_additional_paragraph,
            )

    # Recover old specific paragraph if there isn't during current year
    for e in rules:
        try:
            old_rule = Rule.objects.get(code_year=old_year, n_rule=e.n_rule)
        except Rule.DoesNotExist:
            continue

        if e.has_parag_with_derog and old_rule.has_parag_with_derog:
            old_sp = SpecificParagraph.objects.filter(
                rule_gen_id=old_rule.n_rule, code_year=old_year)
            for s in old_sp:
                if s.training == old_training:
                    r_derog, created = SpecificParagraph.objects.get_or_create(
                        code_year=currentyear().code_year,
                        training=training,
                        rule_gen_id=e.n_rule,
                        paragraph_gen_id=s.paragraph_gen_id
                    )
                    if created:
                        r_derog.type_paragraph = s.type_paragraph
                        r_derog.text_specific_paragraph = s.text_specific_paragraph
                        r_derog.text_motiv = s.text_motiv
                        r_derog.save()
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
    data['parag'] = Paragraph.objects.filter(rule=data['rule'])
    data['specific_paragraph'] = SpecificParagraph.objects.filter(
        code_year=currentyear().code_year, training=t, rule_gen_id=r.n_rule)
    old_specific = SpecificParagraph.objects.filter(
        code_year=currentyear().code_year - 1).filter(rule_gen_id=r.n_rule)
    try:
        old_additional = AdditionalParagraph.objects.filter(
            code_year=currentyear().code_year - 1,
            rule_gen_id=r.n_rule)
    except AdditionalParagraph.DoesNotExist:
        old_additional = None

    can_be_recup = True if r.is_edited == 'N' else False

    data['old_additional'] = True if old_additional and can_be_recup else False
    data['old_specific'] = [
        e.paragraph_gen_id for e in old_specific] if can_be_recup else False

    try:
        data['additional_paragraph'] = AdditionalParagraph.objects.get(
            code_year=currentyear().code_year, training=t, rule_gen_id=r.n_rule)
    except AdditionalParagraph.DoesNotExist:
        pass
    data['specific_ids'] = [
        a.paragraph_gen_id for a in data['specific_paragraph']]

    return render(request, template, data)


def gen_pdf_all_rules(request, training_id):

    year = currentyear().code_year
    training = Training.objects.get(id=training_id)
    r = Rule.objects.filter(
        degree_type=training.degree_type,
        is_in_use=True,
        code_year=currentyear().code_year)
    rules = r.filter(is_eci=True) if training.MECC_type \
        in 'E' else r.filter(is_ccct=True)

    sp = SpecificParagraph.objects.filter(code_year=year, training=training)
    ap = AdditionalParagraph.objects.filter(training=training, code_year=year)
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
    data['training'] = t = Training.objects.get(id=training_id)
    data['title'] = _("Alinéa additionnel")
    data['rule'] = Rule.objects.get(id=rule_id)
    data['from_id'] = rule_id

    rule_gen_id = Rule.objects.get(id=rule_id).n_rule
    old_additional = AdditionalParagraph.objects.filter(
        code_year=currentyear().code_year - 1).get(
            rule_gen_id=n_rule) if old == 'Y' else None
# Create temporary additional; just in order to fill the form with ease
    additional, created = AdditionalParagraph.objects.get_or_create(
        code_year=currentyear().code_year,
        rule_gen_id=rule_gen_id,
        training=t,
    ) if old != "Y" else AdditionalParagraph.objects.get_or_create(
        code_year=currentyear().code_year,
        rule_gen_id=rule_gen_id,
        training=t,
        text_additional_paragraph=old_additional.text_additional_paragraph
    )

    data['form'] = AdditionalParagraphForm(instance=additional)
# Delete th temporary additional if created
    if created:
        additional.delete()

    data['additional'] = _("Vous souhaitez ajouter un alinéa à cette règle pour \
votre formation. Merci de la rédiger ci-dessous :")
    if request.method == 'POST':
        form = AdditionalParagraphForm(request.POST, instance=additional)
        if form.is_valid():
            form.save()
            return redirect(
                'training:specific_paragraph',
                training_id=training_id, rule_id=rule_id)

    return render(request, template, data)


@is_correct_respform
def edit_specific_paragraph(request, training_id, rule_id, paragraph_id, n_rule, old='N', template="training/form/edit_specific_paragraph.html"):
    data = {}

    data['training'] = t = Training.objects.get(id=training_id)
    data['paragraph'] = p = Paragraph.objects.get(id=paragraph_id)
    data['rule'] = r = Rule.objects.get(id=rule_id)
    data['title'] = _("Dérogation")
    data['from_id'] = rule_id

    data['text_derog'] = p.text_derog
    data['text_motiv'] = p.text_motiv
    old_year = currentyear().code_year - 1 if old == "Y" else None
    old_training = Training.objects.get(
        code_year=old_year, n_train=t.n_train) if old == "Y" else None

    try:
        old_sp = SpecificParagraph.objects.get(
            code_year=old_year,
            rule_gen_id=n_rule,
            training=old_training,
            paragraph_gen_id=paragraph_id)
    except SpecificParagraph.DoesNotExist:
        old_sp = None

    sp, created = SpecificParagraph.objects.get_or_create(
        code_year=currentyear().code_year,
        training=t,
        rule_gen_id=r.n_rule,
        paragraph_gen_id=paragraph_id,
    )

    if created:
        sp.text_specific_paragraph = p.text_standard if old_sp is None \
            else old_sp.text_specific_paragraph
        sp.text_motiv = "" if old_sp is None else old_sp.text_motiv
        sp.save()

    data['form'] = SpecificParagraphDerogForm(instance=sp)
    if created:
        sp.delete()
    if request.method == 'POST':
        form = SpecificParagraphDerogForm(request.POST, instance=sp)
        if form.is_valid():
            form.save()
            return redirect(
                'training:specific_paragraph',
                training_id=t.id, rule_id=rule_id)

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


@is_post_request
@login_required
def send_mail(request):
    """
    Send notification mail to des-admin-mecc@unistra.fr
    """

    cc = [request.POST.get('cc')]
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

