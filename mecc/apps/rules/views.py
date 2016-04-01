from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from .models import Rule
from .forms import RuleFormInit
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from mecc.apps.years.models import  UniversityYear
from django.db.models import Q

class RulesListView(ListView):
    model = Rule


class RuleCreate(CreateView):
    model = Rule
    form_class = RuleFormInit
    success_url = '#'
    template_name = 'rules/create/base.html'

    def get_context_data(self, **kwargs):
        context = super(RuleCreate, self).get_context_data(**kwargs)
        try:
            context['latest_id'] = Rule.objects.latest('id').id + 1
        except ObjectDoesNotExist:
            context['latest_id'] = 1

        return context

def edit_rule(request, pk=None, template='rules/create/base.html'):
    data = {}
    data['form_base'] = RuleFormInit
    try:
        data['latest_id'] = Rule.objects.latest('id').id + 1
    except ObjectDoesNotExist:
        data['latest_id'] = 1
    current_year = list(UniversityYear.objects.filter(
        Q(is_target_year=True))).pop(0)
    data['current_year'] = "%s/%s" % (current_year.code_year, current_year.code_year+1)
    if pk != None:
        try:
            rule = Rule.objects.get(id=pk)
            data['old'] = True
        except ObjectDoesNotExist:
            data['old'] = False
            if request.POST:
                rule = Rule.objects.create(label=request.POST.get('label'))
        if request.POST:
            rule.display_order = request.POST.get('display_order')
            rule.label = request.POST.get('label')
            rule.is_in_use = True if request.POST.get('is_in_use') == 'on' else False
            rule.is_edited = request.POST.get('is_edited')
            rule.is_eci = True if request.POST.get('is_eci') == 'on' else False
            rule.is_ccct = True if request.POST.get('is_ccct') == 'on' else False
            rule.code_year = current_year.code_year
            rule.save()

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
