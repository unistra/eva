from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django_cas.decorators import login_required

from mecc.decorators import is_post_request, is_ajax_request
from mecc.apps.degree.models import DegreeType
from mecc.apps.rules.models import Rule, Paragraph
from mecc.apps.rules.forms import RuleForm, AddDegreeTypeToRule, ParagraphForm
from mecc.apps.training.models import SpecificParagraph, AdditionalParagraph, \
    Training
from mecc.apps.utils.pdfs import degree_type_rules, \
    setting_up_pdf, NumberedCanvas, one_rule
from mecc.apps.utils.queries import currentyear
from mecc.apps.mecctable.models import ObjectsLink, StructureObject
from mecc.apps.institute.models import Institute


class RulesListView(ListView):
    """
    Rules list view
    """
    model = Rule

    def get_queryset(self, **args):
        """
        return query rules only for current year
        """
        qs = super(RulesListView, self).get_queryset()
        return qs.filter(code_year=currentyear().code_year if currentyear(
        ) is not None else None)

    def get_context_data(self, **kwargs):
        context = super(RulesListView, self).get_context_data(**kwargs)
        context['degree_types'] = DegreeType.objects.all()
        context['asked_year'] = currentyear().code_year if currentyear(
        ) is not None else None
        return context


class RuleCreate(CreateView):
    """
    Rule create view
    """
    model = Rule
    form_class = RuleForm
    template_name = 'rules/create/base.html'

    def get_success_url(self):
        return reverse('rules:rule_edit', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super(RuleCreate, self).get_context_data(**kwargs)
        current_year = currentyear()
        context['current_year'] = "%s/%s" % (current_year.code_year,
                                             current_year.code_year + 1)
        try:
            context['latest_id'] = Rule.objects.latest('id').id + 1
        except ObjectDoesNotExist:
            context['latest_id'] = 1
        return context


@login_required
def manage_paragraph(request, rule_id,
                     template='rules/manage_paragraph.html', exist=None):
    """
    Paragraph manager view : can create and edit paragraph
    """
    data = {}
    rule = get_object_or_404(Rule, id=rule_id)
    data['rule'] = rule
    current_year = currentyear()
    data['current_year'] = "%s/%s" % (current_year.code_year,
                                      current_year.code_year + 1)
    try:
        data['id_paragraph'] = Paragraph.objects.latest('id').id + 1
    except ObjectDoesNotExist:
        data['id_paragraph'] = 1
    if exist:
        parag = get_object_or_404(Paragraph, id=exist)
        data['paragraph_form'] = ParagraphForm(instance=parag)
        data['id_paragraph'] = parag.id
    else:
        data['paragraph_form'] = ParagraphForm

    if request.POST:
        if exist:
            parag = get_object_or_404(Paragraph, id=exist)
            parag.code_year = current_year.code_year
        else:
            parag = Paragraph.objects.create(
                code_year=current_year.code_year,
                display_order=request.POST.get('display_order'),
                # is_cmp=True if request.POST.get('is_cmp') == 'on' else False,
                is_interaction=True if request.POST.get(
                    'is_interaction') == 'on' else False
            )
        parag.text_standard = request.POST.get('text_standard')
        parag.is_in_use = True if request.POST.get(
            'is_in_use') == 'on' else False
        if not parag.is_in_use and len(parag.specific_involved) > 0:
            data['error'] = parag.specific_involved
            return render(request, template, data)
        parag.display_order = request.POST.get('display_order')
        # parag.is_cmp = True if request.POST.get('is_cmp') == 'on' else False
        parag.is_interaction = True if request.POST.get(
            'is_interaction') == 'on' else False
        parag.text_derog = request.POST.get('text_derog')
        parag.text_motiv = request.POST.get('text_motiv')

        parag.rule.add(rule)
        parag.save()
        return redirect('rules:rule_edit', id=rule.id)

    return render(request, template, data)


@login_required
def edit_paragraph(request, id=None, template='rules/manage_paragraph.html'):
    """
    Edit paragraph view, redirect to paragraph manager
    """
    paragraph = get_object_or_404(Paragraph, id=id)
    _id = paragraph.rule.all()[0].id
    return manage_paragraph(request, rule_id=_id, exist=id)


@login_required
def manage_degreetype(request):
    data = {}
    if request.is_ajax() and request.method == 'POST':
        rule = get_object_or_404(Rule, id=request.POST.get('rule_id'))
        degree_type = DegreeType.objects.get(id=request.POST.get('val'))
        todo = request.POST.get('todo')
        data['degree'] = degree_type.short_label
        data['degree_id'] = degree_type.id
        if todo == 'add':
            rule.degree_type.add(degree_type)
            return JsonResponse(data)

        elif todo == 'del':
            # FIXED : verifie que le customized correspond au type de regle :)
            has_current, customized = rule.has_current_exceptions
            if has_current:
                if degree_type.id in [
                    e.training.degree_type_id for e in customized.get(
                        'specifics') + customized.get('additionals')]:
                    specifics = [e.training.label for e in customized.get(
                        'specifics')]

                    additionals = [e.training.label for e in customized.get(
                        'additionals')]
                    return JsonResponse({
                        'customized': len(customized),
                        'text': ", ".join(specifics + additionals),
                        'specifics': specifics,
                        'additionals': additionals
                    })

            rule.degree_type.remove(degree_type)
            return JsonResponse(data)


@login_required
def update_display_order(request):
    """
    Edit display with ajax
    """
    data = {}
    if request.is_ajax() and request.method == 'POST':
        t = request.POST.get('type')
        if t == 'rule':
            obj = Rule.objects.get(id=request.POST.get('_id'))
        else:
            obj = Paragraph.objects.get(id=request.POST.get('_id'))
        display_order = request.POST.get('display_order')
        obj.display_order = display_order if display_order.isdigit() else 0
        obj.save()
        data['message'] = _("Le numéro d'affichage a bien été mis à jour.")
        data['display_order'] = obj.display_order
        return JsonResponse(data)
    else:
        message = _("L'objet %s n'a pas été mis à jour" %
                    request.POT.get('_id'))
        return JsonResponse({'status': 'False', 'message': message},
                            status=500)


@login_required
def edit_rule(request, id=None, template='rules/create/base.html'):
    """
    Edit rule view
    """
    data = {}

    data['rule'] = rule = get_object_or_404(Rule, id=id)
    request.session['visited_rule'] = rule.id
    data['paragraphs'] = Paragraph.objects.filter(Q(rule=rule))
    data['editing'] = True
    data['form'] = RuleForm(instance=rule)
    data['current_year'] = "%s/%s" % (rule.code_year,
                                      rule.code_year + 1)

    def check_specific():
        derog = SpecificParagraph.objects.filter(
            code_year=rule.code_year,
            rule_gen_id=rule.n_rule)
        additional = AdditionalParagraph.objects.filter(
            code_year=rule.code_year,
            rule_gen_id=rule.n_rule)
        return True if len(additional) + len(derog) != 0 else False

    if request.POST and request.POST.get('label'):
        # form = RuleForm(request.POST, instance=rule)
        # if form.is_valid():
        #     form.save()
        rule.display_order = request.POST.get('display_order')
        rule.label = request.POST.get('label')
        rule.is_in_use = True if request.POST.get(
            'is_in_use') == 'on' else False
        has_current, customs = rule.has_current_exceptions
        if rule.is_in_use is False and has_current:
            rule.is_in_use = True
            data['error'] = customs
        rule.is_edited = request.POST.get('is_edited')
        rule.is_eci = True if request.POST.get('is_eci') == 'on' else False
        rule.is_ccct = True if request.POST.get('is_ccct') == 'on' else False
        rule.code_year = currentyear().code_year
        rule.save()
    data['latest_id'] = rule.id
    data['degreetype_form'] = AddDegreeTypeToRule(instance=rule)
    data['rule_degreetype'] = [e for e in rule.degree_type.all()]
    data['available_degreetype'] = [
        e for e in DegreeType.objects.all() if
        e.id not in [a.id for a in data['rule_degreetype']]  # and
        # not (e.short_label.upper().startswith('CATALOGUE') or
        #      e.long_label.upper().startswith('CATALOGUE'))
    ]

    return render(request, template, data)


class ParagraphDelete(DeleteView):
    """
    Delete paragraph view
    """
    model = Paragraph
    pk_url_kwarg = 'id'
    success_url = '/rules/list'

    def get_success_url(self):
        rule = self.request.session['visited_rule'] if \
            self.request.session['visited_rule'] else self.object.rule.all()[0].id
        return reverse('rules:rule_edit', kwargs={'id': rule})

    def get_context_data(self, **kwargs):
        paragraph = kwargs['object']
        context = super(ParagraphDelete, self).get_context_data(**kwargs)
        context['derog'] = SpecificParagraph.objects.filter(
            paragraph_gen_id=paragraph.id,
            code_year=paragraph.code_year)

        return context


class RuleDelete(DeleteView):
    """
    Delete rule view
    """
    model = Rule
    pk_url_kwarg = 'id'
    success_url = '/rules/list'

    def get_context_data(self, **kwargs):
        rule = kwargs['object']
        context = super(RuleDelete, self).get_context_data(**kwargs)
        context['derog'] = SpecificParagraph.objects.filter(
            rule_gen_id=rule.id, code_year=rule.code_year)
        context['additional'] = AdditionalParagraph.objects.filter(
            rule_gen_id=rule.id, code_year=rule.code_year)
        return context


@login_required
def gen_pdf(request, id_degreetype, year=None):
    year = currentyear().code_year if year is None else int(year)
    degree_type = get_object_or_404(DegreeType, id=id_degreetype)
    title = "MECC - %s - %s" % (
        degree_type.short_label, year)
    response, doc = setting_up_pdf(title, margin=42)
    story = degree_type_rules(title, degree_type, year)

    doc.build(story, canvasmaker=NumberedCanvas)

    return response


@login_required
def gen_all_pdf(request):
    year = currentyear().code_year
    degree_type = get_object_or_404(DegreeType, id=id_degreetype)
    title = "MECC - %s - %s" % (
        degree_type.short_label, year)
    response, doc = setting_up_pdf(title, margin=42)
    story = degree_type_rules(title, degree_type, year)

    doc.build(story, canvasmaker=NumberedCanvas)

    return response


@login_required
def pdf_one_rule(request, rule_id):
    rule = get_object_or_404(Rule, id=rule_id)
    title = "MECC - %s - %s" % (rule.label, rule.code_year)
    response, doc = setting_up_pdf(title, margin=42)
    story = one_rule(title, rule)
    doc.build(story, canvasmaker=NumberedCanvas)
    return response


@login_required
def history_home(request, year=None, template='rules/history.html'):
    data = {}
    year = currentyear().code_year if year is None else year
    data['asked_year'] = int(year)

    all_rules = Rule.objects.all()
    availables_years = sorted({(e.code_year, "%s/%s" % (
        e.code_year, e.code_year + 1)) for e in all_rules}, reverse=True)
    # display current year for selecting year if this year doesn't contain rule
    disp_curr_y = (currentyear().code_year, "%s/%s" % (
        currentyear().code_year, int(currentyear().code_year) + 1))
    if disp_curr_y not in availables_years:
        availables_years.append(disp_curr_y)

    data['availables_years'] = availables_years
    data['rules'] = [(e, Paragraph.objects.filter(
        rule=e)) for e in all_rules.filter(code_year=year)]

    data['degree_types'] = DegreeType.objects.all()

    return render(request, template, data)


@login_required
def duplicate_home(request, year=None, template='rules/duplicate.html'):
    data = {}
    current_year = currentyear()
    data['current_year'] = "%s/%s" % (current_year.code_year,
                                      current_year.code_year + 1)

    all_rules = Rule.objects.all()

    data['availables_years'] = sorted({(e.code_year, "%s/%s" % (
        e.code_year, e.code_year + 1)) for e in all_rules}, reverse=True)
    data['existing_rules'] = current = all_rules.filter(
        code_year=current_year.code_year)
    data['asked_year'] = None if year is None else int(year)

    if year is None:
        return render(request, template, data)
    else:
        rules = all_rules.filter(code_year=year)

    data['rules'] = [e for e in rules if e.n_rule not in [
        a.n_rule for a in current]]
    return render(request, template, data)


@transaction.atomic
@login_required
@is_ajax_request
@is_post_request
def duplicate_add(request):
    """
    Duplicate year -x rule for a selected training
    """

    x = request.POST.getlist('list_id[]')

    dic = [{'year': e.split('_')[0], 'n_rule': e.split('_')[-1]} for e in x]
    labels = []
    rules = Rule.objects.filter(code_year__in={e.get('year') for e in dic})
    old_rules = rules.filter(n_rule__in=[e.get('n_rule') for e in dic])
    paragraphs = Paragraph.objects.filter(
        rule__id__in={e.id for e in old_rules})
    for old_rule in old_rules:
        rule = Rule.objects.create(
            display_order=old_rule.display_order,
            code_year=currentyear().code_year,
            label=old_rule.label,
            is_in_use=old_rule.is_in_use,
            is_edited='N',
            is_eci=old_rule.is_eci,
            is_ccct=old_rule.is_ccct,
            n_rule=old_rule.n_rule
        )

        for old_degree_type in old_rule.degree_type.all():
            rule.degree_type.add(old_degree_type)

        rule.save()

        for p in paragraphs.filter(rule__id=old_rule.id):
            p.origin_parag = p.id
            p.pk = None
            p.code_year = currentyear().code_year
            p.save()
            p.rule.clear()
            p.rule.add(rule)
            p.save()

        labels.append(old_rule.label)

    return JsonResponse({'status': 'added', 'n_rule': [
        e.get('n_rule') for e in dic], 'labels': labels})


@login_required
@is_ajax_request
@is_post_request
def duplicate_remove(request):
    x = request.POST.get('id')
    rule = Rule.objects.get(id=x)
    if rule.has_current_exceptions[0]:
        return JsonResponse({
            "error": "%s comporte des dérogations et/ou \
            alinéas addditionnels" % rule.label
        })
    rule.delete()
    return JsonResponse({"status": "removed", "label": rule.label})


@login_required
@is_ajax_request
def update_progress(request):
    training = Training.objects.get(id=request.POST.get('training_id'))
    _type = request.POST.get('type')
    data = {}
    if _type == "TABLE":
        supply_cmp = Institute.objects.get(code=training.supply_cmp)
        structures = StructureObject.objects.filter(
            owner_training_id=training.id,
            nature__in=['UE', 'EC', 'PT', 'ST']
        )
        if supply_cmp.ROF_support:
            structures = structures.filter(is_existing_rof=True)
        links = ObjectsLink.objects.filter(
            id_child__in=[structure.id for structure in structures],
            id_training=training.id
        )
        if None in [link.coefficient for link in links] and \
                request.POST.get('val') == 'A':
            data['status'] = 409
        else:
            training.progress_table = request.POST.get('val')
            data['status'] = 200
    if _type == "RULE":
        training.progress_rule = request.POST.get('val')
        data['status'] = 200
    training.save()

    data['val'] = _('en cours') if request.POST.get('val') == 'E' else _('achevée')
    return JsonResponse(data)

@login_required
@is_ajax_request
def details_rule(request):
    derog = []

    def gimme_txt(paraid, rulid):
        try:
            o = SpecificParagraph.objects.get(
                paragraph_gen_id=paraid,
                rule_gen_id=rulid,
                code_year=current_year,
                training=training,
            )
        except SpecificParagraph.DoesNotExist:
            return Paragraph.objects.get(id=paraid).text_standard, False

        derog.append(paraid)
        return o.text_specific_paragraph, True

    current_year = currentyear().code_year
    rule_id = request.POST.get('val')
    rule = Rule.objects.get(id=rule_id)
    paragraphs = Paragraph.objects.filter(Q(rule=rule))
    training = Training.objects.get(id=request.POST.get('training_id'))

    # Give required additional paragraph or None
    try:
        additional = AdditionalParagraph.objects.get(
            training=training,
            rule_gen_id=rule_id, code_year=current_year
        )
    except AdditionalParagraph.DoesNotExist:
        additional = None

    specific = True if request.POST.get('type') == 'specific' else False
    json_response = {
        'id': rule_id,
        'year': "%s/%s" % (
            current_year, current_year + 1),
        'title': rule.label,
        'is_specific': specific,
        'paragraphs': [
            {'alinea': e.id,
             'text': e.text_standard if not (
                 e.is_interaction and specific) else gimme_txt(e.id, rule_id)[0],
             'is_derog': gimme_txt(e.id, rule_id)[1],
             'can_be_derog': e.is_interaction,
             'info': _('Dérogation')}
            for e in paragraphs],

    }
    if specific:
        json_response["additional"] = {
            "alinea": "",
            "text": additional.text_additional_paragraph
        } if additional is not None else None

    return JsonResponse(json_response)


@login_required
@is_ajax_request
def details_rules(request):
    derog = []

    def gimme_txt(paraid, rulid):
        try:
            o = SpecificParagraph.objects.get(
                paragraph_gen_id=paraid,
                rule_gen_id=rulid,
                code_year=current_year,
            )
        except SpecificParagraph.DoesNotExist:
            return Paragraph.objects.get(id=paraid).text_standard, False
        except MultipleObjectsReturned:
            return '', False

        derog.append(paraid)
        return o.text_specific_paragraph, True

    current_year = currentyear().code_year
    rule_id = request.POST.get('val')
    rule = Rule.objects.get(id=rule_id)
    paragraphs = Paragraph.objects.filter(Q(rule=rule))
    types = rule.degree_type.all()

    # # Give required additional paragraph or None
    # try:
    #     additional = AdditionalParagraph.objects.get(
    #         training=Training.objects.get(id=request.POST.get('training_id')),
    #         rule_gen_id=x, current_year
    #     )
    # except AdditionalParagraph.DoesNotExist:
    additional = None

    specific = True if request.POST.get('type') == 'specific' else False
    json_response = {
        'id': rule_id,
        'year': "%s/%s" % (
            current_year, current_year + 1),
        'title': rule.label,
        'is_specific': specific,
        'paragraphs': [
            {'alinea': e.id,
             'text': e.text_standard if not (
                 e.is_interaction and specific) else gimme_txt(e.id, rule_id)[0],
             'is_derog': gimme_txt(e.id, rule_id)[1],
             'can_be_derog': e.is_interaction,
             'info': _('Dérogation')}
            for e in paragraphs],
        'degree_types': [e.long_label for e in types],
    }

    if specific:
        json_response["additional"] = {
            "alinea": "",
            "text": additional.text_additional_paragraph
        } if additional is not None else None

    return JsonResponse(json_response)
