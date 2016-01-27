from .models import UniversityYear, InstituteYear
from ..institute.models import Institute
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.utils import timezone
from .forms import UniversityYearForm
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text
from django.shortcuts import redirect, render


class UniversityYearDelete(DeleteView):

    model = UniversityYear

    slug_field = 'code_year'
    slug_url_kwarg = 'code_year'
    success_url = '/years'


class UniversityYearCreate(CreateView):
    # ## Useless as we can use {{object}} in update tempalte view
    # def get_context_data(self, **kwargs):
    #     context = super(UniversityYearCreate, self).get_context_data(**kwargs)
    #     context['create'] = True
    #     return context

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


def initialize_year(request, code_year, template='years/initialize.html'):
    to_process = [
    {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "ART",
        "field": "Arts, Lettres, Langues",
        "label": "Facult\u00e9 des arts"
    },
    "pk": 1
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "LVI",
        "field": "Arts, Lettres, Langues",
        "label": "Facult\u00e9 des langues et des cultures \u00e9trang\u00e8res"
    },
    "pk": 2
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "LGA",
        "field": "Arts, Lettres, Langues",
        "label": "Facult\u00e9 des langues et sciences humaines appliqu\u00e9es (LSHA)"
    },
    "pk": 3
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "LET",
        "field": "Arts, Lettres, Langues",
        "label": "Facult\u00e9 des lettres"
    },
    "pk": 4
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "CPI",
        "field": "Droit, \u00e9conomie, gestion et sciences politiques et sociales",
        "label": "Centre d'\u00e9tudes internationales de la propri\u00e9t\u00e9 intellectuelle (CEIPI)"
    },
    "pk": 5
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "CUJ",
        "field": "Droit, \u00e9conomie, gestion et sciences politiques et sociales",
        "label": "Centre universitaire d'enseignement du journalisme (CUEJ)"
    },
    "pk": 6
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "EMS",
        "field": "Droit, \u00e9conomie, gestion et sciences politiques et sociales",
        "label": "Ecole de management Strasbourg (EM)"
    },
    "pk": 7
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "DRT",
        "field": "Droit, \u00e9conomie, gestion et sciences politiques et sociales",
        "label": "Facult\u00e9 de droit, de sciences politiques et de gestion"
    },
    "pk": 8
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "SEG",
        "field": "Droit, \u00e9conomie, gestion et sciences politiques et sociales",
        "label": "Facult\u00e9 de sciences \u00e9conomiques et de gestion (FSEG)"
    },
    "pk": 9
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "PAG",
        "field": "Droit, \u00e9conomie, gestion et sciences politiques et sociales",
        "label": "Institut de pr\u00e9paration \u00e0 l'administration g\u00e9n\u00e9rale (IPAG)"
    },
    "pk": 10
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "IEP",
        "field": "Droit, \u00e9conomie, gestion et sciences politiques et sociales",
        "label": "Institut d'\u00e9tudes politiques (IEP)"
    },
    "pk": 11
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "ODO",
        "field": "Sant\u00e9",
        "label": "Facult\u00e9 de chirurgie dentaire"
    },
    "pk": 12
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "MED",
        "field": "Sant\u00e9",
        "label": "Facult\u00e9 de m\u00e9decine"
    },
    "pk": 13
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "PHA",
        "field": "Sant\u00e9",
        "label": "Facult\u00e9 de pharmacie"
    },
    "pk": 14
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "EPE",
        "field": "Sciences humaines et sociales",
        "label": "Ecole sup\u00e9rieure du professorat et de l'\u00e9ducation (ESPE)"
    },
    "pk": 15
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "GEO",
        "field": "Sciences humaines et sociales",
        "label": "Facult\u00e9 de g\u00e9ographie et d'am\u00e9nagement"
    },
    "pk": 16
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "PLI",
        "field": "Sciences humaines et sociales",
        "label": "Facult\u00e9 de philosophie"
    },
    "pk": 17
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "PSY",
        "field": "Sciences humaines et sociales",
        "label": "Facult\u00e9 de psychologie"
    },
    "pk": 18
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "EDU",
        "field": "Sciences humaines et sociales",
        "label": "Facult\u00e9 de sciences de l'\u00e9ducation"
    },
    "pk": 19
    } , {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "THC",
        "field": "Sciences humaines et sociales",
        "label": "Facult\u00e9 de th\u00e9ologie catholique"
    },
    "pk": 20
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "THP",
        "field": "Sciences humaines et sociales",
        "label": "Facult\u00e9 de th\u00e9ologie protestante"
    },
    "pk": 21
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "APS",
        "field": "Sciences humaines et sociales",
        "label": "Facult\u00e9 des sciences du sport"
    },
    "pk": 22
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "HIS",
        "field": "Sciences humaines et sociales",
        "label": "Facult\u00e9 des Sciences Historiques"
    },
    "pk": 23
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "SOC",
        "field": "Sciences humaines et sociales",
        "label": "Facult\u00e9 des sciences sociales"
    },
    "pk": 24
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "EOT",
        "field": "Sciences, Technologies",
        "label": "Ecole et observatoire des sciences de la Terre (EOST)"
    },
    "pk": 25
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "ECP",
        "field": "Sciences, Technologies",
        "label": "Ecole europ\u00e9enne de chimie, polym\u00e8res et mat\u00e9riaux (ECPM)"
    },
    "pk": 26
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "ESB",
        "field": "Sciences, Technologies",
        "label": "Ecole sup\u00e9rieure de biotechnologie de Strasbourg (ESBS)"
    },
    "pk": 27
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "CHM",
        "field": "Sciences, Technologies",
        "label": "Facult\u00e9 de chimie"
    },
    "pk": 28
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "VIE",
        "field": "Sciences, Technologies",
        "label": "Facult\u00e9 des sciences de la vie"
    },
    "pk": 29
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "IHA",
        "field": "Sciences, Technologies",
        "label": "Institut universitaire de technologie de Haguenau"
    },
    "pk": 30
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "ISC",
        "field": "Sciences, Technologies",
        "label": "Institut universitaire de technologie Louis Pasteur"
    },
    "pk": 31
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "ILL",
        "field": "Sciences, Technologies",
        "label": "Institut universitaire de technologie Robert Schuman"
    },
    "pk": 32
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "OBS",
        "field": "Sciences, Technologies",
        "label": "Observatoire astronomique de Strasbourg"
    },
    "pk": 33
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "ESP",
        "field": "Sciences, Technologies",
        "label": "T\u00e9l\u00e9com Physique Strasbourg"
    },
    "pk": 34
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "MAI",
        "field": "Sciences, Technologies",
        "label": "UFR de Math\u00e9matique et d'informatique"
    },
    "pk": 35
    }, {
    "model": "institute.institute",
    "fields": {
        "is_on_duty": True,
        "code": "PHI",
        "field": "Sciences, Technologies",
        "label": "UFR physique et ing\u00e9nierie"
    },
    "pk": 36
    }]

    to_add = {
        "dircomp": None,
        "diretu": [],
        "rac": None,
        "scol_manager": [],
    }

    for e in to_process:
        e['fields'].update(to_add)
    data = {}
    print('---------------***********----------------')
    print(to_process)

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

    # if asked_id_cmp == institutes_id_cmp:
    # else:
    #     missing_id_cmp = asked_id_cmp ^ institutes_id_cmp
        # ^ symmetric difference operator (^) give a set of items in either list but not both


    # q = Institute.objects.all()
    # instit_ids = [e.id for e in q]
    #
    # q2 = InstituteYear.objects.all()
    # instit_years = [e.id_cmp for e in q2]
    # initialized_years = set([e.code_year for e in q2])
    # if y.code_year not in initialized_years or len(instit_ids) != len(instit_years) or y != None:
    #     for e in instit_ids:
    #         InstituteYear.objects.create(
    #             id_cmp=e, code_year=code_year
    #         )
    #     y.is_year_init = True
    #     y.save()
