from django.conf.urls import url
from .views import general_dashboard, institute_dashboard
from django_cas.decorators import login_required


urlpatterns = [
    url(r'^$', login_required(general_dashboard),
        name='general'),
    url(r'^institute/(?P<code>\w+)/$', institute_dashboard,
        name='institute'),
]
