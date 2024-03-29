"""
Various year form
"""

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field
from django import forms
from django.forms.widgets import ClearableFileInput
from django.utils.translation import ugettext as _
from mecc.apps.utils.widgets import CustomFileInput
from mecc.apps.years.models import UniversityYear, InstituteYear


class DircompInstituteYearForm(forms.ModelForm):
    """
    Institute year form with fields updatable by directors
    """
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
    """
    University year form with fields updatable by directors
    """
    def __init__(self, *args, **kwargs):
        super(DircompUniversityYearForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-8'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
            Field('date_validation'),
            Field('date_expected')
        )
        if instance and instance.pk:
            self.fields['date_validation'].widget.attrs['readonly'] = True
            self.fields['date_expected'].widget.attrs['readonly'] = True

    class Meta:
        model = UniversityYear
        fields = [
            'date_validation',
            'date_expected',
        ]


class UniversityYearFormCreate(forms.ModelForm):
    """
    University year form
    """
    is_target_year = forms.TypedChoiceField(
        label=_('Cible courante'),
        choices=((0, "Non"), (1, "OUI")),
        coerce=lambda x: bool(int(x)),
        widget=forms.Select,
        required=False,
    )
    is_year_init = forms.CharField(
        max_length=5, min_length=3,
        label=_('Initialisation des composantes effectuée'),
        initial='False', required=False
    )

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
            HTML('<div class="form-group"> <span class=" col-md-5 required-fields blue">\
                        *Champ obligatoire</span>  </div>'),
            HTML('''<hr/>
            <div><label class="control-label col-lg-8" for="id_file">
            %s</label><div class="controls col-lg-4 grey">
            %s</div></div><hr/>''' % (_("Déposer document cadre"), _(
                "Vous devez créer l'année au préalable"))),
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
        ]


class UniversityYearFormUpdate(forms.ModelForm):
    """
    University year form
    """

    is_target_year = forms.TypedChoiceField(
        label=_('Cible courante'),
        choices=((0, "Non"), (1, "OUI")),
        coerce=lambda x: bool(int(x)),
        widget=forms.Select,
        required=False,
    )
    is_year_init = forms.CharField(
        max_length=5, min_length=3,
        label=_('Initialisation des composantes effectuée'),
        initial='False', required=False
    )
    file = forms.FileField(
        label=_("Déposer document cadre"), required=False,
        widget=CustomFileInput()
    )

    file_id = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
    )

    additional_type = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
    )

    instance = None


    def __init__(self, *args, **kwargs):
        super(UniversityYearFormUpdate, self).__init__(*args, **kwargs)

        self.instance = kwargs.get('instance')
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-8'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
                Field('code_year'),
                Field('label_year', readonly=True),
                Field('is_target_year', css_class='input-xlarge'),
                Field('date_validation', css_class='input-xlarge'),
                Field('date_expected', css_class='input-xlarge'),
                Field('file_id', hidden=True),
                Field('additional_type', hidden=True),
                HTML('<div class="form-group"> <span class=" col-md-5 required-fields blue">\
                            *Champ obligatoire</span>  </div>'),
                HTML('<hr/>'),
                Field('file') if kwargs.get('instance') is not
                None else HTML('''
                <div><label class="control-label col-lg-8" for="id_file">
                %s</label><div class="controls col-lg-4 grey">
                %s</div></div>''' % (_("Déposer document cadre"), _(
                    "Vous devez créer l'année au préalable"))),
                HTML('<hr/>'),
                Field('is_year_init', readonly=True),

                HTML('<hr/>'),
        )

        file_initial = self.instance.getPdf()
        if file_initial:
            self.fields['file'].initial = file_initial.file
            self.fields['file_id'].initial = file_initial.id

        for f in self.fields:
            if isinstance(self.fields[f].widget, ClearableFileInput):
                self.fields[f].widget.attrs['accept'] = 'application/pdf'

        self.fields['additional_type'].initial = "doc_cadre"
        
    class Meta:
        model = UniversityYear
        fields = [
            'code_year',
            'label_year',
            'is_target_year',
            'date_validation',
            'date_expected',
            'is_year_init',
        ]


class InstituteYearForm(forms.ModelForm):
    """
    Institute year form
    """
    date_expected_MECC = forms.DateField(
        label=_('Date prévisionnelle Conseil comp. MECC')
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


class DisabledInstituteYearForm(InstituteYearForm):
    """
    Institute year form with disabled fields
    """
    def __init__(self, *args, **kwargs):
        super(DisabledInstituteYearForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        if instance and instance.pk:
            self.fields['date_expected_MECC'].widget.attrs['readonly'] = True
            self.fields['date_last_notif'].widget.attrs['readonly'] = True
