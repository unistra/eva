from django.conf.urls import url
from .views import DegreeListView, DegreeTypeListView, DegreeTypeCreate, \
    DegreeTypeUpdate, DegreeTypeDelete, DegreeCreateView, DegreeUpdateView, DegreeDeleteView
from django_cas.decorators import login_required

urlpatterns = [
    url(r'^list/$', login_required(DegreeListView.as_view()),
        name='list'),
            # url(r'^list/(?P<filter>|all|current)/$', login_required(DegreeListView.as_view()),
            #     name='list'),
    url(r'^create$', login_required(DegreeCreateView.as_view()),
        name='degree_create'),
    url(r'^(?P<id>\d+)', login_required(DegreeUpdateView.as_view()),
        name='degree_edit'),
    url(r'^delete/(?P<id>\d+)', login_required(DegreeDeleteView.as_view()),
        name='degree_delete'),
    url(r'^type/$', login_required(DegreeTypeListView.as_view()),
        name='type'),
    url(r'^type/create$', login_required(DegreeTypeCreate.as_view()),
        name='type_create'),
    url(r'^type/(?P<id>\d+)', login_required(DegreeTypeUpdate.as_view()),
        name='type_edit'),
    url(r'^type/delete/(?P<id>\d+)', login_required(DegreeTypeDelete.as_view()),
        name='type_delete'),
]
