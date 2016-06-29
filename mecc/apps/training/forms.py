from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Div, Submit
from django.utils.translation import ugettext as _
from .models import Training


class InstituteTrainingForm(forms.ModelForm):

    class Meta:
        model = Training
        fields = [
            'institutes',
            'supply_cmp',
        ]

class ValidationTrainingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ValidationTrainingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                'progress_rule',
                'progress_table',
                'date_val_cmp',
                'date_res_des',
                'date_visa_des',
                'date_val_cfvu',
                css_class="training-form training-form-1",
            )
        )

    class Meta:
        model = Training
        fields = [
            'progress_rule',
            'progress_table',
            'date_val_cmp',
            'date_res_des',
            'date_visa_des',
            'date_val_cfvu',
        ]


class TrainingForm(forms.ModelForm):
    """
    Training form
    """
    MECC_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(('E', _('ECI')), ('C', _('CC/CT'))),
        label=_('Régime'), initial='E'
    )
    session_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(('2', _('2 sessions')), (('1', _('Session unique')))),
        label=_('Session'), initial='2'
    )
    label = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'style': 'resize:none;'}),
        label=_("Intitulé de la formation"),
        help_text=_("Année/parcours")
    )

    def __init__(self, *args, **kwargs):
        super(TrainingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(

                'degree_type',

                Div(
                    HTML("""
                        <div class="control-label"> </div>
                        """),
                    'is_used',
                    'MECC_tab',
                    css_class="disp-flex"
                ),
                'label',
                Div(
                    HTML("""
                        <div class="control-label"> </div>
                        """),
                    'MECC_type',
                    'session_type',
                    css_class="disp-flex"
                ),
                'ref_cpa_rof',
                'ref_si_scol',
                Div(
                    Submit('add', _('Valider'),
                           css_class="pull-right btn-warning"),
                ),
                css_class="training-form",
            ),
        )

    class Meta:
        model = Training
        fields = [
            'degree_type',
            'is_used',
            'MECC_tab',
            'label',
            'MECC_type',
            'session_type',
            'ref_cpa_rof',
            'ref_si_scol',
        ]
