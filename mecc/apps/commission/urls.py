from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.home,
        name='home'),
    url(r'^delete/$', views.delete_member,
        name='delete'),
    url(r'^search/$', views.search,
        name='search'),
    url(r'^get_pple/$', views.get_list_of_pple,
        name='get_pple'),
]
