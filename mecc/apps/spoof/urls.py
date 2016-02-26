from django.conf.urls import url
from .views import DES3Edit, DES3Create, home
from mecc.apps.adm.models import Group_DES3


urlpatterns = [
    url(r'^$', home,
        name='home'),
]
