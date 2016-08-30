from django.conf.urls import url
from .views import RulesListView, RuleCreate, RuleDelete, \
    edit_rule, manage_degreetype, update_display_order, pdf_one_rule, \
    manage_paragraph, ParagraphDelete, edit_paragraph, gen_pdf, \
    duplicate_home, duplicate_add, duplicate_remove, history_home, details_rule
from django_cas.decorators import login_required

urlpatterns = [
    url(r'^list/$', login_required(RulesListView.as_view()),
        name='list'),
    url(r'^new/$', login_required(RuleCreate.as_view()),
        name='new'),
    url(r'^delete/(?P<id>\d+)/$', login_required(RuleDelete.as_view()),
        name='rule_delete'),
    url(r'^detail/(?P<id>\d+)/$', edit_rule,
        name='rule_edit'),
    url(r'^manage-degreetype/$', manage_degreetype,
        name='manage_degreetype'),
    url(r'^update-display-order/$', update_display_order,
        name='update_display_order'),
    url(r'^new-paragraph/(?P<rule_id>\d+)/$', manage_paragraph,
        name='manage_paragraph'),
    url(r'^edit-paragraph/(?P<id>\d+)/$', edit_paragraph,
        name='paragraph_edit'),
    url(r'^delete-paragraph/(?P<id>\d+)/$',
        login_required(ParagraphDelete.as_view()),
        name='paragraph_delete'),
    url(r'^gen_pdf/(?P<id_degreetype>\d+)(?:/(?P<year>\d+))?/$', gen_pdf,
        name='gen_pdf'),
    url(r'^gen_one/(?P<rule_id>\d+)/$', pdf_one_rule,
        name='gen_one'),
    # (?:/(?<i>[regex])?/$) makes the arg i optional :)
    url(r'^history(?:/(?P<year>\d+))?/$', history_home,
        name='history'),
    url(r'^duplicate(?:/(?P<year>\d+))?/$', duplicate_home,
        name='duplicate'),
    url(r'^duplicate_add/$', duplicate_add,
        name='duplicate_add'),
    url(r'^duplicate_remove/$', duplicate_remove,
        name='duplicate_remove'),
    url(r'^details_rule/$', details_rule,
        name='details_rule'),
]
