from django.views.generic.list import ListView
from django.views.generic import CreateView
from .models import Training
from .forms import TrainingForm, ValidationTrainingForm
from mecc.apps.utils.querries import currentyear


class TrainingListView(ListView):
    """
    Training list view
    """
    model = Training

    def get_context_data(self, **kwargs):
        context = super(TrainingListView, self).get_context_data(**kwargs)
        context['disp_current_year'] = "%s/%s" % (
            currentyear().code_year, currentyear().code_year + 1)
        return context


class TrainingCreate(CreateView):
    """
    Training year create view
    """
    model = Training
    success_url = '/years'
    form_class = TrainingForm

    def get_context_data(self, **kwargs):
        context = super(TrainingCreate, self).get_context_data(**kwargs)
        context['disp_current_year'] = "%s/%s" % (
            currentyear().code_year, currentyear().code_year + 1)
        return context
