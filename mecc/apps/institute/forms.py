from django import forms
from mecc.apps.institute.models import Institute, AcademicField, Staff, ScolManager
from django.utils.translation import ugettext as _

from django import forms
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions,\
    StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from django.utils.translation import ugettext as _


class InstituteForm(forms.ModelForm):
    field = forms.ModelChoiceField(
        queryset=AcademicField.objects.all(),
        required=True, label=_('Domaine'))

    id_dircomp = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input_prof',
            'readonly': 'readonly'
        }),
        label=_('Directeur de composante'),
        required=False)

    id_rac = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input_adm',
            'readonly': 'readonly'
        }),
        label=_('Responsable administratif'),
        required=False)

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-5'
    helper.field_class = 'col-lg-6'
    helper.form_tag = False
    helper.layout = Layout(
            Field('code'),
            Field('is_on_duty'),
            Field('label'),
            Field('field'),
            Field('id_dircomp'),
            Field('id_rac'),
            Field('diretu'),
            Field('scol_manager'),

    )

    class Meta:
        model = Institute
        exclude = ('rac', 'dircomp')
