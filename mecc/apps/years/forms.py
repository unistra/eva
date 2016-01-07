from django import forms
from mecc.apps.years.models import UniversityYear
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button, Div, Field
from crispy_forms.bootstrap import FormActions
from django.utils.translation import ugettext_lazy as _


class UniversityYearForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UniversityYearForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(

            Div(
                Div('code_year', 'label_year', 'is_target_year',
                    'date_validation', 'date_expected', css_class='col-xs-12'),
                css_class='row'
            )
        )

    class Meta:
        model = UniversityYear
        exclude = ()
