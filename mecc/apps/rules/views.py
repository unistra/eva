from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView
from .models import Rule, Paragraph
from .forms import RuleForm, AddDegreeTypeToRule, ParagraphForm
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from mecc.apps.years.models import UniversityYear
from mecc.apps.degree.models import DegreeType
from django.db.models import Q
from django.core.urlresolvers import reverse
from mecc.apps.degree.models import DegreeType
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from mecc.apps.years.models import UniversityYear
from django_cas.decorators import login_required
from django.http import HttpResponse


from mecc.apps.utils.pdfs import degree_type_rules_for_current_year, \
    setting_up_pdf, NumberedCanvas


class RulesListView(ListView):
    """
    Rules list view
    """
    model = Rule
    def get_queryset(self):
        qs = super(RulesListView, self).get_queryset()
        try:
            current_year = list(UniversityYear.objects.filter(Q(is_target_year=True))).pop(0)
        except IndexError:
            return qs.filter(code_year=1)

        return qs.filter(code_year=current_year.code_year)

    def get_context_data(self, **kwargs):
        context = super(RulesListView, self).get_context_data(**kwargs)
        context['degree_types'] = DegreeType.objects.all()
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
        current_year = list(UniversityYear.objects.filter(
            Q(is_target_year=True))).pop(0)
        context['current_year'] = "%s/%s" % (current_year.code_year, current_year.code_year + 1)
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
    current_year = list(UniversityYear.objects.filter(
        Q(is_target_year=True))).pop(0)
    data['current_year'] = "%s/%s" % (current_year.code_year, current_year.code_year + 1)
    data['id_paragraph'] = Paragraph.objects.latest('id').id + 1

    if exist:
        parag = get_object_or_404(Paragraph, id=exist)
        p = data['paragraph_form'] = ParagraphForm(instance=parag)
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
                is_cmp=True if request.POST.get('is_cmp') == 'on' else False,
                is_interaction=True if request.POST.get('is_interaction') == 'on' else False
            )
        parag.text_standard = request.POST.get('text_standard')
        parag.is_in_use = True if request.POST.get('is_in_use') == 'on' else False
        parag.display_order = request.POST.get('display_order')
        parag.is_cmp = True if request.POST.get('is_cmp') == 'on' else False
        parag.is_interaction = True if request.POST.get('is_interaction') == 'on' else False
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
    print(paragraph.rule.all()[0].id)
    _id = paragraph.rule.all()[0].id
    return manage_paragraph(request, rule_id=_id, exist=id)

@login_required
def manage_degreetype(request):
    # TODO: IS NOT A VIEW
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
        message = _("L'objet %s n'a pas été mis à jour" % request.POT.get('_id'))
        return JsonResponse({'status': 'false', 'message': message}, status=500)

@login_required
def edit_rule(request, id=None, template='rules/create/base.html'):
    """
    Edit rule view
    """
    data = {}

    rule = get_object_or_404(Rule, id=id)

    data['paragraphs'] = Paragraph.objects.filter((Q(rule=rule)))
    data['editing'] = True
    current_year = list(UniversityYear.objects.filter(
        Q(is_target_year=True))).pop(0)
    data['current_year'] = "%s/%s" % (current_year.code_year, current_year.code_year + 1)
    if request.POST and request.POST.get('label'):
        rule.display_order = request.POST.get('display_order')
        rule.label = request.POST.get('label')
        rule.is_in_use = True if request.POST.get('is_in_use') == 'on' else False
        rule.is_edited = request.POST.get('is_edited')
        rule.is_eci = True if request.POST.get('is_eci') == 'on' else False
        rule.is_ccct = True if request.POST.get('is_ccct') == 'on' else False
        rule.code_year = current_year.code_year
        rule.save()
    data['form'] = RuleForm(instance=rule)
    data['latest_id'] = rule.id
    data['degreetype_form'] = AddDegreeTypeToRule(instance=rule)
    data['rule_degreetype'] = [e for e in rule.degree_type.all()]
    data['available_degreetype'] = [
        e for e in DegreeType.objects.all() if
        e.id not in [a.id for a in data['rule_degreetype']] and
        not (e.short_label.upper().startswith('CATALOGUE') or
        e.long_label.upper().startswith('CATALOGUE'))
    ]

    return render(request, template, data)


class ParagraphDelete(DeleteView):
    """
    Delete paragraph view
    """
    model = Paragraph
    pk_url_kwarg = 'id'
    success_url = '/rules/list'


class RuleDelete(DeleteView):
    """
    Delete rule view
    """
    model = Rule
    pk_url_kwarg = 'id'
    success_url = '/rules/list'


def gen_pdf(request, id_degreetype):
    current_year = list(UniversityYear.objects.filter(Q(is_target_year=True))).pop(0)
    degree_type = get_object_or_404(DegreeType, id=id_degreetype)
    title = "MECC - %s - %s" % (degree_type.short_label, current_year.code_year)

    response, doc = setting_up_pdf(title, margin=42)
    story = degree_type_rules_for_current_year(title, degree_type)
    if story is None:
        return redirect('commission:home')
    doc.build(story, canvasmaker=NumberedCanvas)


    return response
