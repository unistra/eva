from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django_cas.decorators import login_required
from mecc.apps.files.models import FileUpload
from mecc.apps.files.utils import create_file
from mecc.apps.institute.models import Institute
from mecc.apps.training.models import Training
from mecc.apps.utils.queries import rules_for_year
from mecc.apps.years.forms import UniversityYearFormUpdate, UniversityYearFormCreate
from mecc.apps.years.models import UniversityYear, InstituteYear
from mecc.decorators import is_ajax_request, is_post_request



@is_ajax_request
def update_is_in_use(request):
    s_year = UniversityYear.objects.get(
        code_year=request.POST.get('code_year'))
    x = True if request.POST.get('value') == '1' else False
    if x and len(UniversityYear.objects.filter(is_target_year=True)) > 0:

        return JsonResponse({
            "status": "error",
            "message": "Veuillez désactiver l'année cible courante",
            })
    else:
        s_year.is_target_year = x
        display = s_year.label_year if x else "Aucune année cible sélectionnée"
        request.session['current_year'] = display
        s_year.save()
        return JsonResponse({
            "status": "updated",
            "message": "%s a été modifiée" % s_year.label_year,
            "display": display
            })


class UniversityYearDelete(DeleteView):
    """
    Univeristy year delete view
    """
    model = UniversityYear

    slug_field = 'code_year'
    slug_url_kwarg = 'code_year'
    success_url = '/years'

    def get_context_data(self, **kwargs):
        code_year = kwargs['object'].code_year
        trainings = Training.objects.filter(code_year=code_year)

        context = super(UniversityYearDelete, self).get_context_data(**kwargs)
        context['rules'] = rules_for_year(code_year) \
            if kwargs['object'].id is not None else None
        context['trainings'] = trainings if len(trainings) > 0 else None
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

    def get_context_data(self, **kwargs):
        context = super(
            UniversityYearUpdate, self).get_context_data(**kwargs)


        return context


    def get_success_url(self):
        if self.request.method == 'POST' and 'add_pdf' in self.request.POST:
            code_year = self.request.POST.get('code_year')

            return reverse('years:edit', kwargs={'code_year': code_year})
        if self.request.method == 'POST' and 'delete_pdf' in self.request.POST:
            code_year = int(self.request.POST.get('code_year'))

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

    def get_queryset(self, **args):
        """
        return query sorted (descending) by code_year
        """
        return super(UniversityYearListView, self).get_queryset().order_by('-code_year')

    model = UniversityYear


@login_required
def initialize_year(request, code_year, template='years/initialize.html'):
    """
    Initialize requested year : create institute year according to
    university year and institute
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
