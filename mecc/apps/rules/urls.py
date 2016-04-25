from django.conf.urls import url
from .views import RulesListView, RuleCreate, RuleDelete, \
    edit_rule, manage_degreetype, update_display_order, \
    manage_paragraph, ParagraphDelete , edit_paragraph
from django_cas.decorators import login_required

urlpatterns = [
    url(r'^list/$', login_required(RulesListView.as_view()),
        name='list'),
    url(r'^new/$', login_required(RuleCreate.as_view()),
        name='new'),
    url(r'^delete/(?P<id>\d+)', login_required(RuleDelete.as_view()),
        name='rule_delete'),
    url(r'^detail/(?P<id>\d+)', edit_rule,
        name='rule_edit'),
    url(r'^manage-degreetype/', manage_degreetype,
        name='manage_degreetype'),
    url(r'^update-display-order/', update_display_order,
        name='update_display_order'),
    url(r'^new-paragraph/(?P<rule_id>\d+)', manage_paragraph,
        name='manage_paragraph'),
    url(r'^edit-paragraph/(?P<id>\d+)', edit_paragraph,
            name='paragraph_edit'),
    url(r'^delete-paragraph/(?P<id>\d+)', login_required(ParagraphDelete.as_view()),
        name='paragraph_delete'),
]
