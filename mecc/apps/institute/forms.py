from django import forms
from mecc.apps.institute.models import Institute, AcademicField, Staff, ScolManager
from django.utils.translation import ugettext_lazy as _

from django import forms
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions,\
    StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from django.utils.translation import ugettext_lazy as _


class InstituteForm(forms.ModelForm):
    field = forms.ModelChoiceField(queryset=AcademicField.objects.all(),
                                   required=True, label=_('Domaine'))
    #
    # dircomp = forms.ModelChoiceField(queryset=Staff.objects.all() if len(Staff.objects.all()) > 0 else ['aucun'],
    #                                  label=_('Directeur de composante'),
    #                                  required=False,)

    # rac = forms.ModelChoiceField(queryset=Staff.objects.all(),
    #                              label=_('Responsable administratif'),
    #                              required=False,)
    #
    # diretu = forms.ModelChoiceField(queryset=Staff.objects.all(),
    #                                 label=("Directeurs d\'études"),
    #                                 required=False,)
    #
    # scol_manager =forms.ModelChoiceField(queryset=ScolManager.objects.all(),
    #                                      label=("Gestionnaires de scolarité"),
    #                                      required=False)

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-5'
    helper.field_class = 'col-lg-6'
    helper.layout = Layout(
            Field('code'),
            Field('is_on_duty'),
            Field('label'),
            Field('field'),
            Field('dircomp'),
            Field('rac'),
            Field('diretu'),
            Field('scol_manager'),

    )

    class Meta:
        model = Institute
        exclude = ()
