from django.utils.translation import ugettext_lazy as _
from mecc.apps.years.models import UniversityYear
from mecc.apps.years.forms import UniversityYearForm
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext

from .forms import UniversityYearForm

from .models import UniversityYear
from django.views.generic.edit import UpdateView


class UniversityYearUpdate(UpdateView):
    model = UniversityYear
    fields = [
        'is_target_year',
        'date_validation',
        'date_expected',
        'is_year_init'
    ]
    template_name_suffix = '_update_form'


def edit(request, code, template='years/create.html'):
    instance = get_object_or_404(UniversityYear, code_year=code)
    form = UniversityYearForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('institute:home')
    return render(request, template, {'form': form}, context_instance=RequestContext(request))


def create(request, template='years/create.html'):
    data = {}
    data['form'] = UniversityYearForm
    return render(request, template, data)


def home(request, template='years/home.html'):
    if request.method == 'POST':
        form = UniversityYearForm(request.POST)
        instance = form.save(commit=False)
        instance.save()
        return redirect('years:home')

    data = {}
    data['years'] = UniversityYear.objects.all()
    data['form'] = UniversityYearForm
    return render(request, template, data)
