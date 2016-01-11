from django.utils.translation import ugettext_lazy as _
from mecc.apps.years.models import UniversityYear
from mecc.apps.years.forms import UniversityYearForm
from django.shortcuts import render, redirect

from .models import UniversityYear
from .forms import UniversityYearForm


def create(request, template='years/create.html'):
    data = {}
    data['form'] = UniversityYearForm
    return render(request, template, data)


def home(request, template='years/home.html'):
    if request.method == 'POST':
        form = UniversityYearForm(request.POST)
        print(form.data['code_year'])
        print(form.data['label_year'])
        print(form.data['date_validation'])
        print(form.data['date_expected'])
        print(form.data['pdf_doc'])
        instance = form.save(commit=False)
        instance.save()
        return redirect('years:home')

    data = {}
    data['years'] = UniversityYear.objects.all()
    data['form'] = UniversityYearForm
    return render(request, template, data)
