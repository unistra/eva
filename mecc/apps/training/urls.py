from django.conf.urls import url
from django_cas.decorators import login_required

from mecc.apps.training.views import TrainingListView, TrainingCreate, \
    TrainingDelete, TrainingEdit, process_respform, list_training, \
    list_training_mecc, respform_list, duplicate_home, duplicate_add, \
    edit_rules, specific_paragraph, update_progress_rule_statut, \
    edit_specific_paragraph, edit_additional_paragraph, ask_delete_specific, \
    delete_specific, recover_everything, gen_pdf_all_rules, send_mail, \
    remove_respform, my_teachings, update_training_regime_session, \
    do_consistency_check, do_regime_session_check, preview_mecc, cancel_transform, reapply_atb, recup_atb_ens
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
    url(r'^list_all_meccs/$', list_training_mecc,
        name='list_all_meccs'),
    url(r'^list_resp/$', respform_list,
        name='list_resp'),
    url(r'^duplicate(?:/(?P<year>\d+))?/$', duplicate_home,
        name='duplicate'),
    url(r'^duplicate_add/$', duplicate_add,
        name='duplicate_add'),
    url(r'^update_progress_rule_statut/$', update_progress_rule_statut,
        name='update_progress_rule_statut'),
    url(r'^edit_rules/(?P<training_id>\d+)/specific_paragraph/(?P<rule_id>\d+)/$',
        specific_paragraph, name='specific_paragraph'),
    url(r'^edit_rules/(?P<training_id>\d+)/specific_paragraph/(?P<rule_id>\d+)/additional/(?P<n_rule>\d+)/(?P<old>\w+)/$',
        edit_additional_paragraph, name='edit_additional_paragraph'),
    url(r'^edit_rules/(?P<training_id>\d+)/specific_paragraph/(?P<rule_id>\d+)/edit/(?P<paragraph_id>\d+)/(?P<n_rule>\d+)/(?P<old>\w+)/$',
        edit_specific_paragraph, name='edit_specific_paragraph'),
    url(r'^ask_delete_specific/$', ask_delete_specific,
        name='ask_delete_specific'),
    url(r'^delete_specific/$', delete_specific,
        name='delete_specific'),
    url(r'^gen_pdf_all_rules/(?P<training_id>\d+)$', gen_pdf_all_rules,
        name='gen_pdf_all_rules'),
    url(r'^send_mail/$', send_mail,
        name='send_mail'),
    url(r'^check_consistency/$', do_consistency_check,
        name='check_consistency'),
    url(r'^remove_respform/$', remove_respform,
        name='remove_respform'),
    url(r'^update_training_regime_session/$', update_training_regime_session,
        name='update_training_regime_session'),
    url(r'^cancel_transform/$', cancel_transform,
        name='cancel_transform'),
    url(r'^my_teachings/$', my_teachings,
        name='my_teachings'),
    url(r'^regime_session_check/$', do_regime_session_check,
        name='regime_session_check'),
    url(r'^preview_mecc/$', preview_mecc,
        name='preview_mecc'),
    url(r'^reapply_atb/$', reapply_atb, name='reapply_atb'),
    url(r'^recup_at_ens/$', recup_atb_ens, name='recup_atb_ens'),
]
