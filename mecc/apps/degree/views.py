from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from .models import Degree, DegreeType
from .forms import DegreeTypeForm, DegreeForm
from django.core.exceptions import ObjectDoesNotExist


class DegreeListView(ListView):
    """
    Degree listview
    """
    model = Degree


class DegreeCreateView(CreateView):
    """
    Degree create view
    """
    model = Degree
    form_class = DegreeForm
    success_url = '/degree/list'


class DegreeUpdateView(UpdateView):
    """
    Degree update view
    """
    model = Degree
    form_class = DegreeForm
    pk_url_kwarg = 'id'
    success_url = '/degree/list'


class DegreeDeleteView(DeleteView):
    """
    Degree delete view
    """
    model = Degree
    pk_url_kwarg = 'id'
    success_url = '/degree/list'

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
