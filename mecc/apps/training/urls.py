from django.conf.urls import url
from .views import TrainingListView, TrainingCreate, TrainingDelete, \
    TrainingEdit, process_respform, list_training, respform_list
from django_cas.decorators import login_required


urlpatterns = [
    url(r'^list(?:/(?P<cmp>\w+))?/$',
        login_required(TrainingListView.as_view()),
        name='list'),
    url(r'^new/$', login_required(TrainingCreate.as_view()),
        name='new'),
    url(r'^delete/(?P<id_training>\w+)', login_required(
        TrainingDelete.as_view()), name='delete'),
    url(r'^edit/(?P<id>\d+)', login_required(TrainingEdit.as_view()),
        name='edit'),
    url(r'^process_resp/$', process_respform,
        name='process_resp'),
    url(r'^list_all/$', list_training,
        name='list_all'),
    url(r'^list_resp/$', respform_list,
        name='list_resp')
    ]
