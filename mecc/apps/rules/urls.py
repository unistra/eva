from django.conf.urls import url
from .views import RulesListView, RuleCreate, create_rule, RuleDelete, \
    edit_rule, play_with_rule, manage_degreetype, update_display_order
from django_cas.decorators import login_required

urlpatterns = [
    url(r'^list/$', login_required(RulesListView.as_view()),
        name='list'),
    url(r'^new/$', RuleCreate.as_view(),
        name='new'),
    url(r'^delete/(?P<id>\d+)', login_required(RuleDelete.as_view()),
        name='rule_delete'),
    url(r'^detail/(?P<id>\d+)', edit_rule,
        name='rule_edit'),
    url(r'^p/', play_with_rule,
        name='play'),
    url(r'^manage-degreetype/', manage_degreetype,
        name='manage_degreetype'),
    url(r'^update-display-order/', update_display_order,
        name='update_display_order'),
]
