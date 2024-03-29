from django.conf.urls import url
from .views import general_dashboard, institute_dashboard, \
    general_derog_pdf, derogations_export_excel, alineas_export_excel, \
    institute_derogations_export_excel, institute_alineas_export_excel
from django_cas.decorators import login_required


urlpatterns = [
    url(r'^$', login_required(general_dashboard),
        name='general'),
    url(r'^institute/(?P<code>\w+)/$', institute_dashboard,
        name='institute'),
    url(r'^general_derog_pdf/$', general_derog_pdf,
        name='general_derog_pdf'),
    url(r'^general_derog_xls/$', derogations_export_excel,
        name='derogations_export_excel'),
    url(r'^general_alineas_xls/$', alineas_export_excel,
        name='alineas_export_excel'),
    url(r'^institute_derog_xls/(?P<code>\w+)$',
        institute_derogations_export_excel,
        name='institute_derogations_export_excel'),
    url(r'^institute_alineas_xls/(?P<code>\w+)$',
        institute_alineas_export_excel,
        name='institute_alineas_export_excel'),
]
