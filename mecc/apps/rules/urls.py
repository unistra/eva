from django.conf.urls import url
from .views import RulesListView, RuleCreate, create_rule
from django_cas.decorators import login_required

urlpatterns = [
    url(r'^list/$', login_required(RulesListView.as_view()),
        name='list'),
    url(r'^new/$', create_rule,
        name='new'),
]
