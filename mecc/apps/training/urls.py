from django.conf.urls import url
from .views import TrainingListView, TrainingCreate
from django_cas.decorators import login_required


urlpatterns = [
    url(r'^list(?:/(?P<cmp>\w+))?/$',
        login_required(TrainingListView.as_view()),
        name='list'),
    url(r'^new/$', login_required(TrainingCreate.as_view()),
        name='new'),
    ]
