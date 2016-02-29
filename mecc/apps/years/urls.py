from django.conf.urls import url
from .views import UniversityYearUpdate, UniversityYearListView, \
    UniversityYearCreate, UniversityYearDelete, initialize_year, \
    InstituteYear2ListView, InstituteYear2Create

urlpatterns = [
    url(r'^(?P<code_year>\d+)', UniversityYearUpdate.as_view(),
        name='edit'),
    url(r'^$', UniversityYearListView.as_view(),
        name='home'),
    url(r'^new/$', UniversityYearCreate.as_view(),
        name='create'),
    url(r'^delete/(?P<code_year>\d+)', UniversityYearDelete.as_view(),
        name='delete'),
    url(r'^initialize/(?P<code_year>\d+)', initialize_year,
        name='initialize'),
    url(r'^v2/list/$', InstituteYear2ListView.as_view(),
        name='list'),
    url(r'^v2/create/$', InstituteYear2Create.as_view(),
        name='create2'),
]
