from django.conf.urls import url
from .views import DegreeListView, DegreeTypeListView, DegreeTypeCreate, \
    DegreeTypeUpdate, DegreeTypeDelete

urlpatterns = [
    url(r'^list/$', DegreeListView.as_view(),
        name='list'),
    url(r'^type/$', DegreeTypeListView.as_view(),
        name='type'),
    url(r'^type/create$', DegreeTypeCreate.as_view(),
        name='type_create'),
    url(r'^type/(?P<id>\d+)', DegreeTypeUpdate.as_view(),
        name='type_edit'),
    url(r'^type/delete/(?P<id>\d+)', DegreeTypeDelete.as_view(),
        name='type_delete'),
]
