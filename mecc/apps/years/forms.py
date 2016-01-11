from django import forms
from mecc.apps.years.models import UniversityYear
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button, Div, Field
from crispy_forms.bootstrap import FormActions
from django.utils.translation import ugettext_lazy as _


class UniversityYearForm(forms.ModelForm):

    class Meta:
        model = UniversityYear
        exclude = ()
