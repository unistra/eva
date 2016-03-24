from django import forms
from django.forms import ModelForm

from .models import Rule
from crispy_forms.bootstrap import InlineCheckboxes, InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Field, Div, Fieldset
from django.utils.translation import ugettext as _

class RuleFormInit(forms.ModelForm):
    EDITED_CHOICES = (
        ('O', _('Oui')),
        ('N', _('Non')),
        ('X', _('Nouvelle')),
    )

    is_edited = forms.ChoiceField(choices=EDITED_CHOICES,
        label=_("La règle a-t-elle été modifiée ?"))

    label = forms.CharField(label=('Libellé de règle'))

    def __init__(self, *args, **kwargs):
        super(RuleFormInit, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                'is_in_use', css_class='init_1'
            ),
            Div(
                Field('label'), css_class='init_2'
            ),
            Div(
                Fieldset(
                "Régime(s) concerné(s) :",
                'is_eci', 'is_ccct'), css_class='init_3'
            ),
            Div(
                'display_order',
                'is_edited' , css_class='init_4'
            )
        )


            # HTML("""
            # <label for="id_degree_type" class="control-label col-md-5">
            #     ID type diplôme <small>(auto)</small>
            # </label>
            # <div class="controls col-md-3">
            #     <input class="form-control" id="id_degree_type" name="id_degree_type" readonly=True>
            # </div>
            #     """),
            # InlineField('is_in_use'),
            # Field('label'),
            # InlineField('is_eci'),
            # InlineField('is_ccct'),
            # Field('display_order'),
            # Field('is_edited'),
    class Meta:
        model = Rule
        fields = [
            'is_in_use',
            'label',
            'is_eci',
            'is_ccct',
            'display_order',
            'is_edited'
        ]
