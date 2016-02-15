from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from .models import Degree, DegreeType
from .forms import DegreeTypeForm
from django.core.exceptions import ObjectDoesNotExist
from fm.views import AjaxFormMixin, AjaxDeleteView, AjaxUpdateView, AjaxCreateView
from django.conf import settings


class DegreeListView(ListView):
    model = Degree


class DegreeTypeListView(ListView):
    model = DegreeType

    def get_context_data(self, **kwargs):
        context = super(DegreeTypeListView, self).get_context_data(**kwargs)
        try:
            context['latest_id'] = DegreeType.objects.latest('id').id + 1
        except ObjectDoesNotExist:
            context['latest_id'] = 1
        return context


class DegreeTypeCreate(AjaxCreateView):
    model = DegreeType
    form_class = DegreeTypeForm

    success_url = '/degree/type'


class DegreeTypeUpdate(AjaxUpdateView):

    model = DegreeType
    form_class = DegreeTypeForm
    pk_url_kwarg = 'id'


class DegreeTypeDelete(AjaxDeleteView):
    model = DegreeType
    pk_url_kwarg = 'id'
