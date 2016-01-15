from django import forms
from mecc.apps.years.models import UniversityYear


class UniversityYearForm(forms.ModelForm):

    class Meta:
        model = UniversityYear
        fields = [
            'code_year',
            'label_year',
            'is_target_year',
            'date_validation',
            'date_expected',
        ]
