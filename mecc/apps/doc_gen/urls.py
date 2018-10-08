from django.conf.urls import url

from .views import home, trainings_for_target, available_target, \
    preview_mecctable, dispatch_to_good_pdf, generate_pdf, history_home, \
    history_for_year, generate_excel_mecctable, generate_rules_docx, \
    published_mecc, generate, get_pdf_task_status, get_pdf

urlpatterns = [
    url(r'^start/$', home, name='home'),
    url(r'^trainings_for_target/$', trainings_for_target,
        name='trainings_for_target'),
    url(r'^available_target/$', available_target,
        name='available_target'),
    # url(r'^mecctable/$', preview_mecctable,
        # name='preview_mecctable'),
    url(r'^dispatch/$', dispatch_to_good_pdf,
        name='dispatch'),
    url(r'^generate_pdf/(?P<task_id>\d+)/$', generate_pdf,
        name='generate_pdf'),
    url(r'^get_pdf_task_status/(?P<task_id>\d+)/$', get_pdf_task_status,
        name='get_pdf_task_status'),
    url(r'^get_pdf/(?P<task_id>\d+)/$', get_pdf,
        name='get_pdf'),
    url(r'^generate/$', generate,
        name='generate'),
    url(r'^history/$', history_home,
        name='history_home'),
    url(r'^history/(?P<year>\d+)/$', history_for_year,
        name='history_year'),
    url(r'^generate_mecctable_excel/$', generate_excel_mecctable, name='mecctable_excel'),
    url(r'^generate_rules_docx/$', generate_rules_docx, name='rules_docx'),
    url(r'^published_mecc/(?P<training_id>\d+)/$', published_mecc, name='published_mecc'),
]
