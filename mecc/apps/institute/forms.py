from django import forms
from mecc.apps.institute.models import Institute, AcademicField
from django.utils.translation import ugettext as _

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Field


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
    helper.field_class = 'col-lg-7'
    helper.layout = Layout(
            Field('code'),
            Field('is_on_duty'),
            Field('label'),
            Field('field'),
            HTML('<hr/>'),
            Field('id_dircomp'),
            Field('id_rac'),
            HTML('<hr/>'),
            Field('diretu'),
            Field('scol_manager'),
            Field('ROF_code'),

    )

    class Meta:
        model = Institute
        fields = [
            'code', 'is_on_duty', 'label', 'field', 'id_dircomp', 'id_rac',
            'diretu', 'scol_manager', 'ROF_code'
        ]


class DircompInstituteForm(InstituteForm):
    def clean_code(self):
        instance = getattr(self, 'instance', None)
        if self.instance:
            return self.instance.code
        else:
            return self.cleaned_data['code']

    def clean_is_on_duty(self):
        instance = getattr(self, 'instance', None)
        if self.instance:
            return self.instance.is_on_duty
        else:
            return self.cleaned_data['is_on_duty']

    def clean_label(self):
        instance = getattr(self, 'instance', None)
        if self.instance:
            return self.instance.label
        else:
            return self.cleaned_data['label']

    def clean_field(self):
        return self.cleaned_data['field']

    def clean_id_dircomp(self):
        instance = getattr(self, 'instance', None)

        return self.cleaned_data['id_dircomp']

    def clean_id_rac(self):
        instance = getattr(self, 'instance', None)
        if self.instance:
            return self.instance.id_rac
        else:
            return self.cleaned_data['id_rac']


    def __init__(self, *args, **kwargs):
        super(DircompInstituteForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['code'].widget.attrs['readonly'] = True
            self.fields['is_on_duty'].widget.attrs['disabled'] = True
            self.fields['label'].widget.attrs['readonly'] = True
            self.fields['field'].widget.attrs['disabled'] = True
            self.fields['id_dircomp'].widget.attrs['readonly'] = True
            self.fields['id_rac'].widget.attrs['readonly'] = True


class RacInstituteForm(DircompInstituteForm):

    def __init__(self, *args, **kwargs):
        super(RacInstituteForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['diretu'].widget.attrs['readonly'] = True
            self.fields['scol_manager'].widget.attrs['disabled'] = True
