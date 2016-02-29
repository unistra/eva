from django.conf.urls import url
from .views import DES3Edit, DES3Create, home, release_user
from mecc.apps.adm.models import Group_DES3


urlpatterns = [
    url(r'^$', home,
        name='home'),
    url(r'^release/$', release_user,
        name='release'),

    ]
