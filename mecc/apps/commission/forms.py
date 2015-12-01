from django import forms
from mecc.apps.commission.models import ECICommissionMember
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button
from crispy_forms.bootstrap import FormActions
from django.utils.translation import ugettext_lazy as _


class ECICommissionMemberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ECICommissionMemberForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Add Commission Member'),
                'id_member',
                'name',
                'member_type',
                'firstname',
            ),
            FormActions(
                Submit('search', _('Search')),
                Button('cancel', _('Cancel'))
            )
        )

    class Meta:
        model = ECICommissionMember
        exclude = ()
