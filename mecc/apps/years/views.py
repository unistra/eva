from .models import UniversityYear
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.utils import timezone


class UniversityYearDelete(DeleteView):
    model = UniversityYear

    slug_field = 'code_year'
    slug_url_kwarg = 'code_year'

    success_url = '/years'


class UniversityYearCreate(CreateView):
    model = UniversityYear
    fields = [
        'code_year',
        'label_year',
        'is_target_year',
        'date_validation',
        'date_expected',
        'pdf_doc',
        'is_year_init'
    ]
    success_url = '/years'


class UniversityYearUpdate(UpdateView):
    model = UniversityYear
    fields = [
        'label_year',
        'is_target_year',
        'date_validation',
        'date_expected',
        'is_year_init'
    ]

    slug_field = 'code_year'
    slug_url_kwarg = 'code_year'

    success_url = '/years'


class UniversityYearListView(ListView):
    model = UniversityYear
