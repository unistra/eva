from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button, Div, Field
from crispy_forms.bootstrap import FormActions
from django.utils.translation import ugettext as _

from .models import ECICommissionMember
from ..adm.models import MeccUser
from django.contrib.auth.models import User


class ECIForm(ModelForm):
    """
    Form allow to create ECI commission member
    """
    MEMBER_TYPE_CHOICES = (
        ('commission', _('Commission ECI')),
        ('tenured', _('Etudiant CFVU titulaire')),
        ('supply', _('Etudiant CFVU suppléant')),
    )

    member_type = forms.ChoiceField(choices=MEMBER_TYPE_CHOICES,
        label=_('Type de membre'))

    def __init__(self, *args, **kwargs):
        super(ECIForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('username'),
            Field('last_name'),
            Field('first_name'),
            Field('member_type'),
            Field('mail')
        )

    class Meta:
        model = ECICommissionMember
        fields = ['username', 'member_type', 'last_name', 'first_name', 'email']
