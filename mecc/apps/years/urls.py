from django.conf.urls import url
from .views import UniversityYearUpdate, UniversityYearListView, \
    UniversityYearCreate, UniversityYearDelete, initialize_year

urlpatterns = [
    # url(r'^$', views.home,
    #     name='home'),
    # url(r'^create/$', views.create,
    #     name='create'),
    # url(r'^(?P<code>\d+)', views.edit,
    #     name='edit'),
    url(r'^(?P<code_year>\d+)', UniversityYearUpdate.as_view(),
        name='edit'),
    url(r'^$', UniversityYearListView.as_view(),
        name='home'),
    url(r'^new/$', UniversityYearCreate.as_view(),
        name='create'),
    url(r'^delete/(?P<code_year>\d+)', UniversityYearDelete.as_view(),
        name='delete'),
    url(r'intialise/', initialize_year, name='initialize')
]
