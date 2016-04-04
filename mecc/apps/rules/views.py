from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from .models import Rule
from .forms import RuleFormInit, AddDegreeTypeToRule
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
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


def get_list_of_pple(request):
    data = {}
    if request.is_ajax():
        x = request.GET.get('member', '')
        if len(x) > 1:
            ppl = [e for e in get_from_ldap(x) if e['username'] not in [e.username for e in ECICommissionMember.objects.all()]]
            data['pple'] = sorted(ppl, key=lambda x: x['first_name'])
            return JsonResponse(data)
        else:
            return JsonResponse({'message': _('Veuillez entrer au moins deux caractères.')})

# TODO: faire en sort
def manage_degreetype(request):
    data = {}
    if request.is_ajax() and request.method == 'POST':
        rule = Rule.objects.get(id=request.POST.get('rule_id'))
        degree_type = DegreeType.objects.get(id=request.POST.get('val'))
        todo = request.POST.get('todo')
        if todo == 'add':
            rule.degree_type.add(degree_type)

            return JsonResponse({'message': _('%s a bien été ajouté à %s.' % (degree_type.short_label, rule.label)) })

        elif todo == 'del':
            rule.degree_type.remove(degree_type)
            return JsonResponse({'message': _('%s a bien été supprimé de %s.' % (degree_type.short_label, rule.label)) })


def edit_rule(request, id=None, template='rules/create/base.html'):
    data = {}
    rule = Rule.objects.get(id=id)
    data['editing'] = True
    current_year = list(UniversityYear.objects.filter(
        Q(is_target_year=True))).pop(0)
    data['current_year'] = "%s/%s" % (current_year.code_year, current_year.code_year+1)
    if request.POST:
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

def play_with_rule(request, id=None, template='rules/create/base.html'):
    current_year = list(UniversityYear.objects.filter(
            Q(is_target_year=True))).pop(0)
    data = {}
    try:
        rule = Rule.objects.get(id=id)
        data['old'] = True
    except ObjectDoesNotExist:
        data['old'] = False

    if data['old'] == True:
        data['rule_display_order'] = rule.display_order
        data['latest_id'] = rule.id
        data['rule_label'] = rule.label
        data['rule_is_in_use'] = rule.is_in_use
        data['rule_is_edited'] = rule.is_edited
        data['rule_is_eci'] = rule.is_eci
        data['rule_is_ccct'] = rule.is_ccct

    if request.POST:
        display_order = int(request.POST.get('rule_diplay_order'))
        label = request.POST.get('rule_label')
        is_in_use = True if request.POST.get('rule_is_in_use') == 'on' else False
        is_edited = request.POST.get('rule_is_edited')
        is_eci = True if request.POST.get('rule_is_eci') == 'on' else False
        is_ccct = True if request.POST.get('rule_is_ccct') == 'on' else False
        if is_eci or is_ccct:
            rule.display_order = int(request.POST.get('rule_diplay_order'))
            rule.code_year = current_year.code_year
            rule.label = request.POST.get('rule_label')
            rule.is_in_use =  True if request.POST.get('rule_is_in_use') == 'on' else False
            rule.is_edited = request.POST.get('rule_is_edited')
            rule.is_eci = True if request.POST.get('rule_is_eci') == 'on' else False
            rule.is_ccct = True if request.POST.get('rule_is_ccct') == 'on' else False
            rule.save()
    current_year = current_year.code_year
    data['current_year'] = "%s/%s" % (current_year, current_year+1)
    try:
        data['latest_id'] = Rule.objects.latest('id').id + 1
    except ObjectDoesNotExist:
        data['latest_id'] = 1

    return render(request, template, data)


def create_rule(request, template='rules/create/base.html'):
    current_year = list(UniversityYear.objects.filter(
            Q(is_target_year=True))).pop(0)
    data = {}
    data['form_base'] = RuleFormInit

    if request.POST:
        display_order = request.POST.get('display_order')
        label = request.POST.get('label')
        is_in_use = True if request.POST.get('is_in_use') == 'on' else False
        is_edited = request.POST.get('is_edited')
        is_eci = True if request.POST.get('is_eci') == 'on' else False
        is_ccct = True if request.POST.get('is_ccct') == 'on' else False
        if is_eci or is_ccct:
            rule = Rule.objects.create(
                display_order=display_order,
                code_year=current_year.code_year,
                label=label,
                is_in_use=is_in_use,
                is_edited=is_edited,
                is_eci=is_eci,
                is_ccct=is_ccct
            )
            rule.save()
        return redirect('/rules/list') # Redirect after POST

    current_year = current_year.code_year
    data['current_year'] = "%s/%s" % (current_year, current_year+1)
    try:
        data['latest_id'] = Rule.objects.latest('id').id + 1
    except ObjectDoesNotExist:
        data['latest_id'] = 1
    return render(request, template, data)


class RuleDelete(DeleteView):
    model = Rule
    pk_url_kwarg = 'id'
    success_url = '/rules/list'
