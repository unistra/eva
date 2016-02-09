from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'mecc.views.home', name='home'),
    url(r'^commission/', include('mecc.apps.commission.urls',
        namespace='commission')),
    url(r'^years/', include('mecc.apps.years.urls',
        namespace='years')),
    url(r'^institute/', include('mecc.apps.institute.urls',
        namespace='institute')),
    url(r'^admin/', include(admin.site.urls)),

)

# debug toolbar for dev
if settings.DEBUG and 'debug_toolbar'in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
