from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from .models import Degree, DegreeType
from .forms import DegreeTypeForm, DegreeForm
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from mecc.apps.years.models import UniversityYear
from mecc.apps.institute.models import Institute
from mecc.apps.utils.queries import rules_since_ever
from mecc.apps.training.models import Training
import operator
from functools import reduce


class DegreeListView(ListView):
    """
    Degree listview
    """
    model = Degree
    template_name = 'degree/degree_list.html'

    def get_queryset(self):
        if self.kwargs['filter'] == 'all':
            degrees = Degree.objects.all()
        elif self.kwargs['filter'] == 'current':
            current_year = list(UniversityYear.objects.filter(
                Q(is_target_year=True))).pop(0).code_year
            degrees = Degree.objects.filter(
                Q(end_year__gte=current_year, start_year__lte=current_year))

        if self.kwargs['cmp'] in [e.code for e in Institute.objects.all()]:
            return degrees.filter(institutes__code=self.kwargs['cmp'])
        else:
            return degrees

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['institutes'] = Institute.objects.all()
        context['cmp'] = self.kwargs['cmp']
        return context


class DegreeCreateView(CreateView):
    """
    Degree create view
    """
    model = Degree
    form_class = DegreeForm
    success_url = '/degree/list/all/none'


class DegreeUpdateView(UpdateView):
    """
    Degree update view
    """
    model = Degree
    form_class = DegreeForm
    pk_url_kwarg = 'id'
    success_url = '/degree/list/all/none'


class DegreeDeleteView(DeleteView):
    """
    Degree delete view
    """
    model = Degree
    pk_url_kwarg = 'id'
    success_url = '/degree/list/all/none'


class DegreeTypeListView(ListView):
    """
    Degree type listview
    """
    model = DegreeType


class DegreeTypeCreate(CreateView):
    """
    Degree type create view
    """
    model = DegreeType
    form_class = DegreeTypeForm
    success_url = '/degree/type'

    def get_context_data(self, **kwargs):
        context = super(DegreeTypeCreate, self).get_context_data(**kwargs)
        try:
            context['latest_id'] = DegreeType.objects.latest('id').id + 1
        except ObjectDoesNotExist:
            context['latest_id'] = 1

        return context


class DegreeTypeUpdate(UpdateView):
    """
    Degree type update view
    """
    model = DegreeType
    form_class = DegreeTypeForm
    pk_url_kwarg = 'id'
    success_url = '/degree/type'


class DegreeTypeDelete(DeleteView):
    """
    Degree type delete view
    """
    model = DegreeType
    pk_url_kwarg = 'id'
    success_url = '/degree/type'

    def get_context_data(self, **kwargs):
        context = super(DegreeTypeDelete, self).get_context_data(**kwargs)
        trainings = Training.objects.filter(degree_type=kwargs['object'])
        context['trainings'] = trainings if len(trainings) > 0 else None
        context['rules'] = r = rules_since_ever(
            kwargs['object'].id) if kwargs['object'].id is not None else None 
        if r:
            _all = [e.has_current_exceptions[1] for e in
                    r if e.has_current_exceptions[0] is True]
            additionals = []
            specifics = []
            [(additionals.append(e.get('additionals')),
              specifics.append(e.get('specifics'))) for e in _all]
            context['additionals'] = reduce(operator.concat, additionals)
            context['specifics'] = reduce(operator.concat, specifics)
        return context
