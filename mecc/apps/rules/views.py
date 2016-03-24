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


def create_rule(request, template='rules/create/base.html'):
    current_year = list(UniversityYear.objects.filter(
            Q(is_target_year=True))).pop(0)
    data = {}

    if request.POST:
        print("asking stuff ....")
        display_order = int(request.POST.get('rule_diplay_order'))
        label = request.POST.get('rule_label')
        is_in_use = True if request.POST.get('rule_is_in_use') == 'on' else False
        is_edited = request.POST.get('rule_is_edited')
        is_eci = True if request.POST.get('rule_is_eci') == 'on' else False
        is_ccct = True if request.POST.get('rule_is_ccct') == 'on' else False
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
        print("asked")

    current_year = current_year.code_year
    data['current_year'] = "%s/%s" % (current_year, current_year+1)

    return render(request, template, data)
