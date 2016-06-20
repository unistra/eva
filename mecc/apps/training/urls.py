from django.conf.urls import url
from .views import home, release_user, spoof_user


urlpatterns = [
    url(r'^$', home,
        name='home'),
    url(r'^release/$', release_user,
        name='release'),
    url(r'^spoof/$', spoof_user,
        name='spoof'),
    ]
