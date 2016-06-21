from django.views.generic.list import ListView
from django.views.generic import CreateView
from .models import Training
from .forms import TrainingForm


class TrainingListView(ListView):
    """
    Training list view
    """
    model = Training


class TrainingCreate(CreateView):
    """
    Training year create view
    """
    model = Training
    success_url = '/years'
    form_class = TrainingForm
