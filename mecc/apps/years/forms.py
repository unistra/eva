from django import forms
from mecc.apps.years.models import UniversityYear, InstituteYear
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from django.utils.translation import ugettext as _


class DircompInstituteYearForm(forms.ModelForm):
    date_expected_MECC = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={'class': 'datepicker'}),
        label=_('Date prévisionnelle Conseil comp. MECC')
    )

    def __init__(self, *args, **kwargs):
        super(DircompInstituteYearForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-8'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
            Field('date_expected_MECC'),
            Field('date_last_notif'),
            FormActions(
                Submit('add', _('Valider'), css_class="pull-right"),
            )
        )
        if instance and instance.pk:
                self.fields['date_last_notif'].widget.attrs['readonly'] = True

    class Meta:
        model = InstituteYear
        fields = [
            'date_expected_MECC',
            'date_last_notif',
        ]


class DircompUniversityYearForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DircompUniversityYearForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-8'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
            # Field('pdf_code'),
            Field('date_validation'),
            Field('date_expected')
        )
        if instance and instance.pk:
            self.fields['date_validation'].widget.attrs['readonly'] = True
            self.fields['date_expected'].widget.attrs['readonly'] = True

    class Meta:
        model = UniversityYear
        fields = [
            # 'pdf_doc',
            'date_validation',
            'date_expected',
        ]


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
    helper.label_class = 'col-lg-8'
    helper.field_class = 'col-lg-4'
    helper.layout = Layout(
            Field('code_year'),
            Field('label_year', readonly=True),
            Field('is_target_year', css_class='input-xlarge'),
            Field('date_validation', css_class='input-xlarge'),
            Field('date_expected', css_class='input-xlarge'),
            HTML('<hr/>'),
            Field('pdf_doc', readonly=True),
            HTML("""
            <a href="#" class="btn btn-primary" id="upload_doc">%s </a>
            """ % _('Déposer le document cadre')),
            HTML('<hr/>'),
            Field('is_year_init', readonly=True),

            HTML('<hr/>'),

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


class InstituteYearForm(forms.ModelForm):
    date_expected_MECC = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'datepicker'})
    )

    def __init__(self, *args, **kwargs):
        super(InstituteYearForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-8'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
            Field('date_expected_MECC'),
            Field('date_last_notif')
        )

    class Meta:
        model = InstituteYear
        fields = [
            'date_expected_MECC',
            'date_last_notif',
        ]


class RacInstituteYearForm(InstituteYearForm):
    def __init__(self, *args, **kwargs):
        super(RacInstituteYearForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        if instance and instance.pk:
            self.fields['date_expected_MECC'].widget.attrs['readonly'] = True
            self.fields['date_last_notif'].widget.attrs['readonly'] = True
