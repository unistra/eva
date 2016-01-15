from .models import UniversityYear
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
            a = UniversityYear.objects.get(is_target_year=True).label_year
        except ObjectDoesNotExist:
            a = str(_('Aucune année cible sélectionnée'))
        context['current_year'] = a
        self.request.session['current_year'] = a
        return context

    model = UniversityYear
