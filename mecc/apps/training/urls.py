from django.conf.urls import url
from .views import TrainingListView, TrainingCreate, TrainingDelete, \
    TrainingEdit
from django_cas.decorators import login_required


urlpatterns = [
    url(r'^list(?:/(?P<cmp>\w+))?/$',
        login_required(TrainingListView.as_view()),
        name='list'),
    url(r'^new/$', login_required(TrainingCreate.as_view()),
        name='new'),
    url(r'^delete/(?P<id_training>\w+)', login_required(
        TrainingDelete.as_view()), name='delete'),
    url(r'^edit/(?P<id>\d+)', TrainingEdit.as_view(),
        name='edit'),
    ]
