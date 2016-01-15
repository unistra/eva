from .models import UniversityYear, InstituteYear
from ..institute.models import Institute
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.utils import timezone
from .forms import UniversityYearForm
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text


class UniversityYearDelete(DeleteView):
    model = UniversityYear

    slug_field = 'code_year'
    slug_url_kwarg = 'code_year'

    success_url = '/years'


class UniversityYearCreate(CreateView):
    model = UniversityYear
    form_class = UniversityYearForm
    success_url = '/years'


class UniversityYearUpdate(UpdateView):
    model = UniversityYear
    fields = [
        'code_year',
        'label_year',
        'is_target_year',
        'date_validation',
        'date_expected',
    ]

    slug_field = 'code_year'
    slug_url_kwarg = 'code_year'

    success_url = '/years'


class UniversityYearListView(ListView):
    def get_context_data(self, **kwargs):
        context = super(UniversityYearListView, self).get_context_data(**kwargs)
        try:
            a = UniversityYear.objects.get(is_target_year=True)
        except ObjectDoesNotExist:
            a = str(_('Aucune année cible sélectionnée'))
        self.request.session['current_year'] = a.label_year
        self.request.session['current_code_year'] = a.code_year
        return context

    model = UniversityYear


def initialize_year(request):
    try:
        y = UniversityYear.objects.get(code_year=request.session['current_code_year'])
    except ObjectDoesNotExist:
        y = None

    q = Institute.objects.all()
    list_id_institutes = [e.id for e in q]

    for e in list_id_institutes:
        InstituteYear.objects.create(id_cmp=e, code_year=request.session['current_code_year'])
