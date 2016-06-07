from .models import UniversityYear, InstituteYear
from ..institute.models import Institute
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from .forms import UniversityYearFormUpdate, UniversityYearFormCreate
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.shortcuts import render
from django_cas.decorators import login_required
from mecc.apps.utils.querries import rules_for_year
from mecc.decorators import is_ajax_request, is_post_request
from django.shortcuts import redirect
from django.core.urlresolvers import reverse


class UniversityYearDelete(DeleteView):
    """
    Univeristy year delete view
    """
    model = UniversityYear

    slug_field = 'code_year'
    slug_url_kwarg = 'code_year'
    success_url = '/years'

    def get_context_data(self, **kwargs):
        context = super(UniversityYearDelete, self).get_context_data(**kwargs)
        context['rules'] = rules_for_year(kwargs['object'].code_year) \
            if kwargs['object'].id is not None else None
        return context


class UniversityYearCreate(CreateView):
    """
    University year create view
    """
    model = UniversityYear
    form_class = UniversityYearFormCreate
    success_url = '/years'


class UniversityYearUpdate(UpdateView):
    """
    University year update view
    """
    model = UniversityYear
    form_class = UniversityYearFormUpdate

    slug_field = 'code_year'
    slug_url_kwarg = 'code_year'

    def get_success_url(self):
        if self.request.method == 'POST' and 'add_pdf' in self.request.POST:
            code_year = self.request.POST.get('code_year')
            return reverse('years:edit', kwargs={'code_year': code_year})
        return reverse('years:home')


class UniversityYearListView(ListView):
    """
    University year list view
    """
    def get_context_data(self, **kwargs):
        context = super(
            UniversityYearListView, self).get_context_data(**kwargs)
        try:
            a = UniversityYear.objects.get(is_target_year=True)
        except ObjectDoesNotExist:
            a = str(_('Aucune année cible sélectionnée'))
        try:
            self.request.session['current_year'] = a.label_year
            self.request.session['current_code_year'] = a.code_year
        except AttributeError:
            self.request.session['current_year'] = str(
                _('Aucune année cible sélectionnée'))
            self.request.session['current_code_year'] = None

        return context

    model = UniversityYear


@login_required
def initialize_year(request, code_year, template='years/initialize.html'):
    """
    Initialize requested year : create institute year according to
    university year and instiute
    """
    data = {}
    try:
        y = UniversityYear.objects.get(code_year=code_year)
    except ObjectDoesNotExist:
        data['message'] = _(
            "L'année universitaire demandée n'a pas été trouvée.")
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


@is_post_request
@is_ajax_request
def delete_pdf(request):
    x = request.POST.get('id_year', '')
    uy = UniversityYear.objects.get(id=x)
    uy.pdf_doc.delete(save=False)
    uy.save()
    return redirect('years:edit', code_year=uy.code_year)
