from django import forms
from mecc.apps.commission.models import ECICommission
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button
from crispy_forms.bootstrap import FormActions
from django.utils.translation import ugettext_lazy as _


class ECICommissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ECICommissionForm, self).__init__(*args, **kwargs)
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
        model = ECICommission
        exclude = ()
