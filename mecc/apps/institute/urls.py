from django.conf.urls import url
from . import views
from .views import InstituteCreate, InstituteUpdate, InstituteDelete, \
    InstituteListView,  get_list, edit_insitute, dircomp_edit_institute, view_institute
from django.views.generic.list import ListView
from .models import Institute
from django_cas.decorators import login_required


urlpatterns = [
    url(r'^$', login_required(InstituteListView.as_view()),
        name='home'),
    url(r'^new/$', login_required(InstituteCreate.as_view()),
        name='create'),
    url(r'^details/(?P<code>\w+)', login_required(InstituteUpdate.as_view()),
        name='edit'),
    url(r'^rac/(?P<code>\w+)', view_institute,
        name='rac_edit'),
    url(r'^dircomp/(?P<code>\w+)', dircomp_edit_institute,
        name='dircomp_edit'),
    url(r'^delete/(?P<code>\w+)', login_required(InstituteDelete.as_view()),
        name='delete'),
    url(r'^ressources/(?P<employee_type>|prof|adm|stud)/(?P<pk>[a-zA-Z]{3})',
        get_list, name='get_list'),
    url(r'^modify/(?P<code>\w+)', edit_insitute,
        name='modify'),

]
