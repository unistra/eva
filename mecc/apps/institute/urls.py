from django.conf.urls import url
from . import views
from .views import InstituteCreate, InstituteUpdate
from django.views.generic.list import ListView
from .models import Institute


urlpatterns = [
    # url(r'^$', views.home,
    #     name='home'),
    # url(r'^(?P<code>\w+)', views.edit,
    #     name='edit'),
    # url(r'^create/$', views.create,
    #     name='create'),
    url(r'^$', ListView.as_view(
            model=Institute,
            template_name='institute/institute_list.html'),
        name='home'),
    url(r'^new/$', InstituteCreate.as_view(),
        name='create'),
    url(r'^(?P<code>\w+)', InstituteUpdate.as_view(),
        name='edit'),
]
