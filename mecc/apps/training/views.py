from django.views.generic.list import ListView
from .models import Training


class TrainingListView(ListView):
    """
    Training list view
    """
    model = Training
