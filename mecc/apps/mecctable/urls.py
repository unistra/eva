from django.conf.urls import url
from .views import StructureObjectListView, StructureObjectCreateView, \
    StructureObjectDetailView, StructureObjectUpdateView, \
    ObjectsLinkListView, ObjectsLinkCreateView, ObjectsLinkDetailView, \
    ObjectsLinkUpdateView, ExamListView, ExamCreateView, ExamDetailView, \
    ExamUpdateView, mecctable_home, mecctable_update, remove_object, \
    get_stuct_obj_details, update_grade_coeff, get_mutual_by_cmp, \
    import_objectslink, remove_imported, get_consom, update_mecc_position, \
    send_mail_respform, copy_old_mecctable2, list_exams, add_exam, update_exam, \
    delete_exam, copy_exam_1_to_2, copy_old_exams


urlpatterns = [
    url(r'^send_mail_respform/$', send_mail_respform,
        name='send_mail_respform'),
    url(r'^imported/remove/(?P<id>\d+)$',
        remove_imported,
        name='remove_imported'),

    url(r'^get_mutual_by_cmp/$',
        get_mutual_by_cmp,
        name='get_mutual_by_cmp'),

    url(r'^update_mecc_position/$',
        update_mecc_position,
        name='update_mecc_position'),

    url(r'^get_consom/$',
        get_consom,
        name='get_consom'),

    url(r'^training/(?P<id>\w+)/$',
        mecctable_home,
        name='mecctable_home'),

    url(r'^mecctable_update/$',
        mecctable_update,
        name='mecctable_update'),
    url(r'^get_stuct_obj_details/$',
        get_stuct_obj_details,
        name='get_stuct_obj_details'),
    url(r'^update_grade_coeff/$',
        update_grade_coeff,
        name='update_grade_coeff'),

    # urls for StructureObject
    url(r'^structureobject/$',
        StructureObjectListView.as_view(),
        name='mecctable_structureobject_list'),
    url(r'^structureobject/create/$',
        StructureObjectCreateView.as_view(),
        name='mecctable_structureobject_create'),
    url(r'^structureobject/detail/(?P<id>\d+)/$',
        StructureObjectDetailView.as_view(),
        name='mecctable_structureobject_detail'),
    url(r'^structureobject/update/(?P<id>\d+)/$',
        StructureObjectUpdateView.as_view(),
        name='mecctable_structureobject_update'),
    url(r'^structureobject/remove/(?P<id>\d+)$',
        remove_object,
        name='remove_structureobject'),

    # urls for ObjectsLink
    url(r'^import_objectslink/$', import_objectslink,
        name='import_objectslink'),
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
    # AJAX way
    url(r'^list_exams/(?P<id_structure>\d+)$',
        list_exams,
        name='list_exams'),
    url(r'^add_exam/$',
        add_exam,
        name='add_exam'),
    url(r'^update_exam/(?P<id_structure>\d+)$',
        update_exam,
        name='update_exam'),
    url(r'^delete_exam/(?P<id_structure>\d+)$',
        delete_exam,
        name='delete_exam'),
    url(r'^copy_exam_1_to_2/(?P<id_structure>\d+)$',
        copy_exam_1_to_2,
        name='copy_exam_1_to_2'),

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

    url(r'^copy_old_mecctable/$',
        copy_old_mecctable2,
        name='copy_old_mecctable'),
    url(r'^copy_old_exams/$',
        copy_old_exams,
        name='copy_old_exams'),

]
