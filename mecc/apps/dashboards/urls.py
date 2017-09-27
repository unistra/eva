from django.conf.urls import url
from .views import general_dashboard
from django_cas.decorators import login_required


urlpatterns = [
    url(r'^$', login_required(general_dashboard),
        name='general'),
]
