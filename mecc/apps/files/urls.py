from django.conf.urls import url

from .views import upload_file, delete_file

urlpatterns = [
    url(r'^upload/(?P<app_name>\w+)/(?P<model_name>\w+)/(?P<object_pk>\d+)$',
        upload_file, name='upload_file'),
    url(r'^delete/(?P<file_id>\d+)$',
        delete_file, name='delete_file'),
]
