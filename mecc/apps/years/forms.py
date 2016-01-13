from django import forms
from mecc.apps.years.models import UniversityYear


class UniversityYearForm(forms.ModelForm):

    class Meta:
        model = UniversityYear
        exclude = ('',)
