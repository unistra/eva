from django.conf.urls import url
from .views import DES3Edit
from mecc.apps.adm.models import Group_DES3


urlpatterns = [
    url(r'^details/', DES3Edit.as_view(),
        name='edit'),
]
