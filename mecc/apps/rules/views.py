from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView
from .models import Rule, Paragraph
from .forms import RuleFormInit, AddDegreeTypeToRule, ParagraphForm
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from mecc.apps.years.models import  UniversityYear
from django.db.models import Q
from django.core.urlresolvers import reverse
from mecc.apps.degree.models import DegreeType
from django.http import JsonResponse
from django.utils.translation import ugettext as _


class RulesListView(ListView):
    model = Rule


class RuleCreate(CreateView):
    model = Rule
    form_class = RuleFormInit
    template_name = 'rules/create/base.html'

    def get_success_url(self):
        return reverse('rules:rule_edit', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super(RuleCreate, self).get_context_data(**kwargs)
        current_year = list(UniversityYear.objects.filter(
            Q(is_target_year=True))).pop(0)
        context['current_year'] = "%s/%s" % (current_year.code_year, current_year.code_year+1)
        try:
            context['latest_id'] = Rule.objects.latest('id').id + 1
        except ObjectDoesNotExist:
            context['latest_id'] = 1
        return context


def manage_paragraph(request, rule_id,
    template='rules/manage_paragraph.html', exist=None):
    data = {}
    rule = get_object_or_404(Rule, id=rule_id)
    data['rule'] = rule
    current_year = list(UniversityYear.objects.filter(
        Q(is_target_year=True))).pop(0)
    data['current_year'] = "%s/%s" % (current_year.code_year, current_year.code_year+1)

    if request.POST:
        parag = Paragraph.objects.create(
            code_year=current_year.code_year,
            text_standard=request.POST.get('text_standard'),
            is_in_use=True if request.POST.get('is_in_use') == 'on' else False,
            display_order=request.POST.get('display_order'),
            is_cmp=True if request.POST.get('is_cmp') == 'on' else False,
            is_interaction=True if request.POST.get('is_interaction') == 'on' else False,
            text_derog=request.POST.get('text_derog'),
            text_motiv=request.POST.get('text_motiv'),
            # impact= ,
        )
        parag.rule.add(rule)
        parag.save()
        # return edit_rule(request, id=rule.id, redir=True) # Redirect after POST
        return redirect('rules:rule_edit', id=rule.id)

    if exist:
        paragraph = get_object_or_404(Paragraph, id=exist)
        data['paragraph_form'] = ParagraphForm(instance=paragraph)
    else:
        data['paragraph_form'] = ParagraphForm

    try:
        data['id_paragraph'] = Paragraph.objects.latest('id').id + 1
    except ObjectDoesNotExist:
        data['id_paragraph'] = 1

    return render(request, template, data)

def edit_paragraph(request, id=None,  template='rules/manage_paragraph.html'):
    paragraph = get_object_or_404(Paragraph, id=id)
    print(paragraph.rule.all()[0].id)
    _id = paragraph.rule.all()[0].id
    return manage_paragraph(request, rule_id=_id, exist=id)


def manage_degreetype(request):
    data = {}
    if request.is_ajax() and request.method == 'POST':
        rule =  get_object_or_404(Rule, id=request.POST.get('rule_id'))
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

def update_display_order(request):
    data = {}
    if request.is_ajax() and request.method == 'POST':
        t = request.POST.get('type')
        if t == 'rule':
            obj = Rule.objects.get(id=request.POST.get('_id'))
        else :
            obj = Paragraph.objects.get(id=request.POST.get('_id'))
        display_order = request.POST.get('display_order')
        obj.display_order = display_order if display_order.isdigit() else 0
        obj.save()
        data['message'] = _("Le numéro d'affichage a bien été mis à jour.")
        data['display_order'] = obj.display_order
        return JsonResponse(data)
    else :
        message = _("L'objet %s n'a pas été mis à jour" % request.POT.get('_id'))
        return JsonResponse({'status':'false','message':message}, status=500)

def edit_rule(request, id=None, template='rules/create/base.html'):
    data = {}

    rule = get_object_or_404(Rule, id=id)

    data['paragraphs'] = Paragraph.objects.filter((Q(rule=rule)))
    data['editing'] = True
    current_year = list(UniversityYear.objects.filter(
        Q(is_target_year=True))).pop(0)
    data['current_year'] = "%s/%s" % (current_year.code_year, current_year.code_year+1)
    if request.POST and request.POST.get('label'):
        rule.display_order = request.POST.get('display_order')
        rule.label = request.POST.get('label')
        rule.is_in_use = True if request.POST.get('is_in_use') == 'on' else False
        rule.is_edited = request.POST.get('is_edited')
        rule.is_eci = True if request.POST.get('is_eci') == 'on' else False
        rule.is_ccct = True if request.POST.get('is_ccct') == 'on' else False
        rule.code_year = current_year.code_year
        rule.save()
    data['form'] = RuleFormInit(instance=rule)
    data['latest_id'] = rule.id
    data['degreetype_form'] = AddDegreeTypeToRule(instance=rule)
    data['rule_degreetype'] = [e for e in rule.degree_type.all()]
    data['available_degreetype'] = [e for e in DegreeType.objects.all() if e.id not in [a.id for a in data['rule_degreetype']] ]


    return render(request, template, data)




#
# def play_with_rule(request, id=None, template='rules/create/base.html'):
#     current_year = list(UniversityYear.objects.filter(
#             Q(is_target_year=True))).pop(0)
#     data = {}
#     try:
#         rule = Rule.objects.get(id=id)
#         data['old'] = True
#     except ObjectDoesNotExist:
#         data['old'] = False
#
#     if data['old'] == True:
#         data['rule_display_order'] = rule.display_order
#         data['latest_id'] = rule.id
#         data['rule_label'] = rule.label
#         data['rule_is_in_use'] = rule.is_in_use
#         data['rule_is_edited'] = rule.is_edited
#         data['rule_is_eci'] = rule.is_eci
#         data['rule_is_ccct'] = rule.is_ccct
#
#     if request.POST:
#         display_order = int(request.POST.get('rule_diplay_order'))
#         label = request.POST.get('rule_label')
#         is_in_use = True if request.POST.get('rule_is_in_use') == 'on' else False
#         is_edited = request.POST.get('rule_is_edited')
#         is_eci = True if request.POST.get('rule_is_eci') == 'on' else False
#         is_ccct = True if request.POST.get('rule_is_ccct') == 'on' else False
#         if is_eci or is_ccct:
#             rule.display_order = int(request.POST.get('rule_diplay_order'))
#             rule.code_year = current_year.code_year
#             rule.label = request.POST.get('rule_label')
#             rule.is_in_use =  True if request.POST.get('rule_is_in_use') == 'on' else False
#             rule.is_edited = request.POST.get('rule_is_edited')
#             rule.is_eci = True if request.POST.get('rule_is_eci') == 'on' else False
#             rule.is_ccct = True if request.POST.get('rule_is_ccct') == 'on' else False
#             rule.save()
#     current_year = current_year.code_year
#     data['current_year'] = "%s/%s" % (current_year, current_year+1)
#     try:
#         data['latest_id'] = Rule.objects.latest('id').id + 1
#     except ObjectDoesNotExist:
#         data['latest_id'] = 1
#
#     return render(request, template, data)


class ParagraphDelete(DeleteView):
    model = Paragraph
    pk_url_kwarg = 'id'
    success_url = '/rules/list'


class RuleDelete(DeleteView):
    model = Rule
    pk_url_kwarg = 'id'
    success_url = '/rules/list'
