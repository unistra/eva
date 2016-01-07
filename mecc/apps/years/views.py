from django.utils.translation import ugettext_lazy as _
from mecc.apps.years.models import UniversityYear
from mecc.apps.years.forms import UniversityYearForm
from django.shortcuts import render


def home(request, template='years/home.html'):
    data = {}
    data['years'] = UniversityYear.objects.all()
    data['form'] = UniversityYearForm
    return render(request, template, data)
