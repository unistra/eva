from django.conf.urls import url
from .views import InstituteCreate, InstituteUpdate, InstituteDelete, \
    InstituteListView,  edit_institute, granted_edit_institute, \
    add_pple, remove_pple, validate_institute, send_mail
from django_cas.decorators import login_required


urlpatterns = [
    url(r'^$', login_required(InstituteListView.as_view()),
        name='home'),
    url(r'^new/$', login_required(InstituteCreate.as_view()),
        name='create'),
    url(r'^details/(?P<code>\w+)/$', login_required(InstituteUpdate.as_view()),
        name='edit'),
    url(r'^granted/(?P<code>\w+)/$', granted_edit_institute,
        name='dircomp_edit'),
    url(r'^delete/(?P<code>\w+)/$', login_required(InstituteDelete.as_view()),
        name='delete'),
    url(r'^modify/(?P<code>\w+)/$', edit_institute,
        name='modify'),
    url(r'^add_pple/$', add_pple,
        name="add_pple"),
    url(r'^remove_pple/$', remove_pple,
        name="remove_pple"),
    url(r'^send_mail/$', send_mail,
        name='send_mail'),
    url(r'^validate/(?P<code>\w+)/$', validate_institute,
        name='validate'),
]
