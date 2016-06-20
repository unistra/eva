from django.conf.urls import url
from .views import TrainingListView
from django_cas.decorators import login_required


urlpatterns = [
    url(r'^list/$', login_required(TrainingListView.as_view()),
        name='list'),
    ]
