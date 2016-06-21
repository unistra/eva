from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Field, Div, Submit
from django.utils.translation import ugettext as _

from .models import Training


class TrainingForm(forms.ModelForm):
    """
    Training form
    """
    def __init__(self, *args, **kwargs):
        super(TrainingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Div(
                Div(

                    Div(
                        'degree_type',
                    ),
                    Div(
                        'is_used',
                        'MECC_tab',
                    ),
                    Div(
                        'label',
                    ),
                    Div(
                        'MECC_type',
                    ),
                    Div(
                        'session_type',
                    ),
                    Div(
                        'ref_cpa_rof',
                    ),
                    Div(
                        'ref_si_scol',
                    ),
                    Div(
                        Submit(
                            'add', _('Valider'),
                            ),
                    ),
                ),
                style="width:50%;background-color: yellow;"
            )

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
