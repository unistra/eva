from django import forms
from mecc.apps.institute.models import Institute, AcademicField
from django.utils.translation import ugettext_lazy as _


class InstituteForm(forms.ModelForm):
    # field = forms.ModelChoiceField(queryset=AcademicField.objects.all(),
    #                                required=True, label=_('Domaine'))

    class Meta:
        model = Institute
        exclude = ()
