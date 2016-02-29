from .models import UniversityYear, InstituteYear, InstituteYear2
from ..institute.models import Institute
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.utils import timezone
from .forms import UniversityYearForm, InstituteYear2Form
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text
from django.shortcuts import redirect, render
from fm.views import AjaxCreateView

from django_cas.decorators import login_required

class InstituteYear2Create(AjaxCreateView):
    form_class = InstituteYear2Form

class InstituteYear2ListView(ListView):
    model = InstituteYear2

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

@login_required
def initialize_year(request, code_year, template='years/initialize.html'):
    data = {}
    try:
        y = UniversityYear.objects.get(code_year=code_year)
    except ObjectDoesNotExist:
        data['message'] = _("L'année universitaire demandée n'a pas été trouvée.")
        return render(request, '500.html', data)
    except KeyError as e:
        data['message'] = e.message
        return render(request, '500.html', data)

    institutes = Institute.objects.all()
    asked_instit_years = InstituteYear.objects.filter(code_year=code_year)

    asked_id_cmp = set([e.id_cmp for e in asked_instit_years])
    institutes_id_cmp = set([e.id for e in institutes])

    missing_id_cmp = asked_id_cmp ^ institutes_id_cmp

    if len(missing_id_cmp) is 0:
        data['message'] = _("L'initialisation des composantes est à jour.")
        return render(request, template, data)
    else:
        x = 0
        for e in missing_id_cmp:
            InstituteYear.objects.create(id_cmp=e, code_year=code_year)
            x += 1
        y.is_year_init = True
        y.save()
        if x == 1:
            data['message'] = _('1 composante a été initialisée.')
        else:
            data['message'] = _('%s composantes ont été initialisées.' % x)

    return render(request, template, data)
