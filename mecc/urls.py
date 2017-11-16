from django.conf.urls import patterns, include, url
from django.conf import settings
from django_cas.decorators import login_required
from django.conf.urls.static import static
from mecc.apps.institute.views import get_list
from mecc.apps.files.views import serve_file
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'mecc.views.home', name='home'),
    url(r'^commission/', include('mecc.apps.commission.urls',
        namespace='commission')),
    url(r'^years/', include('mecc.apps.years.urls',
        namespace='years')),
    url(r'^dashboards/', include('mecc.apps.dashboards.urls',
        namespace='dashboards')),
    url(r'^doc_gen/', include('mecc.apps.doc_gen.urls',
        namespace='doc_gen')),
    url(r'^mecctable/', include('mecc.apps.mecctable.urls',
        namespace='mecctable')),
    url(r'^degree/', include('mecc.apps.degree.urls',
        namespace='degree')),
    url(r'^institute/', include('mecc.apps.institute.urls',
        namespace='institute')),
    url(r'^spoof/', include('mecc.apps.spoof.urls',
        namespace='spoof')),
    url(r'^rules/', include('mecc.apps.rules.urls',
        namespace='rules')),
    url(r'^file/', include('mecc.apps.files.urls',
        namespace='files')),
    url(r'^ressources/(?P<employee_type>|prof|adm|all)/(?P<pk>[a-zA-Z]{3}).json',
        get_list, name='get_list'),
    url(r'^training/', include('mecc.apps.training.urls',
        namespace='training')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django_cas.views.login'),
    (r'^accounts/logout/$', 'django_cas.views.logout'),
    url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
        serve_file, {'document_root': settings.MEDIA_ROOT}),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# debug toolbar for dev
if settings.DEBUG and 'debug_toolbar'in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
