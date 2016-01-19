from .models import UniversityYear, InstituteYear
from ..institute.models import Institute
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.utils import timezone
from .forms import UniversityYearForm
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text
from django.shortcuts import redirect


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
    form_class = UniversityYearForm


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
        try:
            self.request.session['current_year'] = a.label_year
            self.request.session['current_code_year'] = a.code_year
        except AttributeError:
            self.request.session['current_year'] = str(_('Aucune année cible sélectionnée'))
            self.request.session['current_code_year'] = None

        return context

    model = UniversityYear


def initialize_year(request):
    try:
        y = UniversityYear.objects.get(code_year=request.session['current_code_year'])
    except (ObjectDoesNotExist, KeyError):
        return redirect('years:home')
    q = Institute.objects.all()
    instit_ids = [e.id for e in q]

    q2 = InstituteYear.objects.all()
    instit_years = [e.id_cmp for e in q2]
    initialized_years = set([e.code_year for e in q2])
    print(y.code_year)
    if y.code_year not in initialized_years or len(instit_ids) != len(instit_years) or y != None:
        for e in instit_ids:
            InstituteYear.objects.get_or_create(
                id_cmp=e, code_year=request.session['current_code_year']
            )
        y.is_year_init = True
        y.save()


    return redirect('years:home')
