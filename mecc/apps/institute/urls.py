from django.conf.urls import url
from . import views
from .views import InstituteCreate, InstituteUpdate, InstituteDelete, \
    InstituteListView,  get_list, edit_insitute, granted_edit_institute, \
    add_pple, remove_pple
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
    url(r'^granted/(?P<code>\w+)', granted_edit_institute,
        name='dircomp_edit'),
    url(r'^delete/(?P<code>\w+)', login_required(InstituteDelete.as_view()),
        name='delete'),
    url(r'^ressources/(?P<employee_type>|prof|adm|stud)/(?P<pk>[a-zA-Z]{3})',
        get_list, name='get_list'),
    url(r'^modify/(?P<code>\w+)', edit_insitute,
        name='modify'),
    url(r'^add_pple/$', add_pple,
        name="add_pple"),
    url(r'^remove_pple/$', remove_pple,
        name="remove_pple"),

]
