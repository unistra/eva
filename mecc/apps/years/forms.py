from django import forms
from mecc.apps.years.models import UniversityYear, InstituteYear2
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from django.utils.translation import ugettext as _


class UniversityYearForm(forms.ModelForm):
    is_target_year = forms.TypedChoiceField(
        label=_('Cible courante'),
        choices=((0, "Non"), (1, "OUI")),
        coerce=lambda x: bool(int(x)),
        widget=forms.Select,
        required=True,
    )
    is_year_init = forms.CharField(
        max_length=5, min_length=3,
        label=_('Initialisation des composantes effectuée'),
        initial='False',
    )
    pdf_doc = forms.CharField(
        widget=forms.Textarea(attrs={'rows':4, 'cols':40}),
        label=_('Documents pdf'), required=False)

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-5'
    helper.field_class = 'col-lg-6'
    helper.layout = Layout(
            Field('code_year'),
            Field('label_year', readonly=True),
            Field('is_target_year', css_class='input-xlarge'),
            Field('date_validation', css_class='input-xlarge'),
            Field('date_expected', css_class='input-xlarge'),
            Field('is_year_init', readonly=True),
            Field('pdf_doc', readonly=True),
    )

    class Meta:
        model = UniversityYear
        fields = [
            'code_year',
            'label_year',
            'is_target_year',
            'date_validation',
            'date_expected',
            'is_year_init',
            'pdf_doc'
        ]


class InstituteYear2Form(forms.ModelForm):
    class Meta:
        model = InstituteYear2
        exclude = ()
