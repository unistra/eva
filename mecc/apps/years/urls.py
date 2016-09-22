from django.conf.urls import url
from .views import UniversityYearUpdate, UniversityYearListView, \
    UniversityYearCreate, UniversityYearDelete, initialize_year, \
    update_is_in_use
from django_cas.decorators import login_required


urlpatterns = [
    url(r'^(?P<code_year>\d+)', login_required(UniversityYearUpdate.as_view()),
        name='edit'),
    url(r'^$', login_required(UniversityYearListView.as_view()),
        name='home'),
    url(r'^new/$', login_required(UniversityYearCreate.as_view()),
        name='create'),
    url(r'^delete/(?P<code_year>\d+)', login_required(
        UniversityYearDelete.as_view()), name='delete'),
    url(r'^initialize/(?P<code_year>\d+)', initialize_year,
        name='initialize'),
    url(r'^update_is_in_use', update_is_in_use,
        name='update_is_in_use')
]
