from django.conf.urls import url
from .views import RulesListView, RuleCreate, create_rule, RuleDelete, \
    edit_rule, play_with_rule
from django_cas.decorators import login_required

urlpatterns = [
    url(r'^list/$', login_required(RulesListView.as_view()),
        name='list'),
    url(r'^new/$', create_rule,
        name='new'),
    url(r'^delete/(?P<id>\d+)', login_required(RuleDelete.as_view()),
        name='rule_delete'),
    url(r'^detail/(?P<pk>\d+)', edit_rule,
        name='rule_edit'),
    url(r'^p/', play_with_rule,
        name='play'),
]
