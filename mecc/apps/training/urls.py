from django.conf.urls import url
from .views import TrainingListView, TrainingCreate, TrainingDelete, \
    TrainingEdit, process_respform, list_training, respform_list, \
    duplicate_home, duplicate_add, duplicate_remove, edit_rules, \
    specific_paragraph, update_progress_rule_statut, edit_specific_paragraph, \
    edit_additional_paragraph, ask_delete_specific, delete_specific, \
    recover_everything, gen_pdf_all_rules, send_mail
from django_cas.decorators import login_required
from mecc.decorators import is_correct_respform

urlpatterns = [
    url(r'^list(?:/(?P<cmp>\w+))?/$',
        login_required(TrainingListView.as_view()),
        name='list'),
    url(r'^new/$', login_required(TrainingCreate.as_view()),
        name='new'),
    url(r'^delete/(?P<id_training>\w+)/$', login_required(
        TrainingDelete.as_view()), name='delete'),
    url(r'^edit/(?P<id>\d+)/$', is_correct_respform(TrainingEdit.as_view()),
        name='edit'),
    url(r'^edit_rules/(?P<id>\d+)/$', edit_rules,
        name='edit_rules'),
    url(r'^recover_everything/(?P<training_id>\d+)/$', recover_everything,
        name='recover_everything'),
    url(r'^process_resp/$', process_respform,
        name='process_resp'),
    url(r'^list_all/$', list_training,
        name='list_all'),
    url(r'^list_resp/$', respform_list,
        name='list_resp'),
    url(r'^duplicate(?:/(?P<year>\d+))?/$', duplicate_home,
        name='duplicate'),
    url(r'^duplicate_add/$', duplicate_add,
        name='duplicate_add'),
    url(r'^update_progress_rule_statut/$', update_progress_rule_statut,
        name='update_progress_rule_statut'),
    url(r'^duplicate_remove/$', duplicate_remove,
        name='duplicate_remove'),
    url(r'^edit_rules/(?P<training_id>\d+)/specific_paragraph/(?P<rule_id>\d+)/$',
        specific_paragraph, name='specific_paragraph'),
    url(r'^edit_rules/(?P<training_id>\d+)/specific_paragraph/(?P<rule_id>\d+)/additional/(?P<n_rule>\d+)/(?P<old>\w+)/$',
        edit_additional_paragraph, name='edit_additional_paragraph'),
    url(r'^edit_rules/(?P<training_id>\d+)/specific_paragraph/(?P<rule_id>\d+)/edit/(?P<paragraph_id>\d+)/(?P<n_rule>\d+)//(?P<old>\w+)/$',
        edit_specific_paragraph, name='edit_specific_paragraph'),
    url(r'^ask_delete_specific/$', ask_delete_specific,
        name='ask_delete_specific'),
    url(r'^delete_specific/$', delete_specific,
        name='delete_specific'),
    url(r'^gen_pdf_all_rules/(?P<training_id>\d+)$', gen_pdf_all_rules,
        name='gen_pdf_all_rules'),
    url(r'^send_mail/$', send_mail,
        name='send_mail'),
]
