from django.conf.urls import url

from .views import home, trainings_for_target, available_target

urlpatterns = [
    url(r'^start/$', home, name='home'),
    url(r'^trainings_for_target/$', trainings_for_target,
        name='trainings_for_target'),
    url(r'^available_target/$', available_target,
        name='available_target'),        
]
