from django import forms
from mecc.apps.commission.models import ECICommissionMember
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button, Div, Field
from crispy_forms.bootstrap import FormActions
from django.utils.translation import ugettext_lazy as _


class ECICommissionMemberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ECICommissionMemberForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(

            Div(
                Div(Field('name', readonly=True), css_class='col-xs-6'),
                Div(Field('firstname', readonly=True), css_class='col-xs-6'),
                css_class='row'),

            Div(
                Div(Field('id_member', readonly=True), css_class='col-xs-6'),
                Div(Field('mail', readonly=True), css_class='col-xs-6'),
                css_class='row'),

            Div(
                Div('member_type', css_class='col-xs-12'),
                css_class='row'),

            FormActions(
                Submit('add', _('Add')),
                Button('cancel', _('Cancel'), data_dismiss='modal')
            )
        )

    class Meta:
        model = ECICommissionMember
        exclude = ()
