from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.home,
        name='home'),
    url(r'^delete/$', views.delete_member,
        name='delete'),
    url(r'^get_pple/$', views.get_list_of_pple,
        name='get_pple'),
    url(r'^change_typemember/$', views.change_typemember,
        name='change_typemember'),
    url(r'^send_mail/$', views.send_mail,
        name='send_mail'),
]
