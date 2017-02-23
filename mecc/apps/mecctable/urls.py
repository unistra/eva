from django.conf.urls import url
from .views import StructureObjectListView, StructureObjectCreateView, \
    StructureObjectDetailView, StructureObjectUpdateView, \
    ObjectsLinkListView, ObjectsLinkCreateView, ObjectsLinkDetailView, \
    ObjectsLinkUpdateView, ExamListView, ExamCreateView, ExamDetailView, \
    ExamUpdateView, mecctable_home, mecctable_update

urlpatterns = [
    url(r'^training/(?P<id>\w+)/$', mecctable_home,
        name='mecctable_home'),
    url(r'^mecctable_update/$',
        mecctable_update,
        name='mecctable_update'),

    # urls for StructureObject
    url(r'^structureobject/$',
        StructureObjectListView.as_view(),
        name='mecctable_structureobject_list'),
    url(r'^structureobject/create/$',
        StructureObjectCreateView.as_view(),
        name='mecctable_structureobject_create'),
    url(r'^structureobject/detail/(?P<id>\S+)/$',
        StructureObjectDetailView.as_view(),
        name='mecctable_structureobject_detail'),
    url(r'^structureobject/update/(?P<id>\S+)/$',
        StructureObjectUpdateView.as_view(),
        name='mecctable_structureobject_update'),

    # urls for ObjectsLink
    url(r'^objectslink/$', ObjectsLinkListView.as_view(),
        name='mecctable_objectslink_list'),
    url(r'^objectslink/create/$',
        ObjectsLinkCreateView.as_view(),
        name='mecctable_objectslink_create'),
    url(r'^objectslink/detail/(?P<id>\S+)/$',
        ObjectsLinkDetailView.as_view(),
        name='mecctable_objectslink_detail'),
    url(r'^objectslink/update/(?P<id>\S+)/$',
        ObjectsLinkUpdateView.as_view(),
        name='mecctable_objectslink_update'),

    # urls for Exam
    url(r'^exam/$', ExamListView.as_view(),
        name='mecctable_exam_list'),
    url(r'^exam/create/$', ExamCreateView.as_view(),
        name='mecctable_exam_create'),
    url(r'^exam/detail/(?P<id>\S+)/$',
        ExamDetailView.as_view(),
        name='mecctable_exam_detail'),
    url(r'^exam/update/(?P<id>\S+)/$',
        ExamUpdateView.as_view(),
        name='mecctable_exam_update'),
]
