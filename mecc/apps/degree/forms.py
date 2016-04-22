from django import forms
from .models import DegreeType
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, Div, Field, \
    HTML
from crispy_forms.bootstrap import InlineField, FormActions

from django.utils.translation import ugettext as _

class DegreeForm(forms.ModelForm):
    """
    Degree form
    """

    def __init__(self, *args, **kwargs):
        super(DegreeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout



class DegreeTypeForm(forms.ModelForm):
    """
    Degree type form
    """
    def __init__(self, *args, **kwargs):
        super(DegreeTypeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-5'
        self.helper.field_class = 'col-md-7'
        self.render_hidden_fields = True
        self.render_unmentioned_fields = True
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        HTML("""
                    <label for="id_degree_type" class="control-label col-md-5">
                        ID type diplôme <small>(auto)</small>
                    </label>
                    <div class="controls col-md-3">
                        <input class="form-control" id="id_degree_type" name="id_degree_type" readonly=True>
                    </div>
                            """),
                        InlineField('is_in_use'),
                        css_class='col-md-12'
                        ),
                    css_class='row'
                    ),
                Div(
                    Div(Field('display_order'), css_class='col-md-12'),
                    css_class="row"
                ),
                Div(
                    Div(Field('short_label'), css_class='col-md-12'),
                    css_class="row"
                ),
                Div(
                    Div(Field('long_label'), css_class='col-md-12'),
                    css_class="row"
                ),
                Div(
                    Div(Field('ROF_code'),
                        css_class='col-md-12'),
                    css_class="row"
                ),
                Div(
                    FormActions(
                        Button(
                            'cancel', 'Annuler', onclick='history.go(-1);',
                            css_class='pull-right btn btn-default'),
                        Submit(
                            'add', _('Valider'), css_class="pull-right",
                            style="margin-right:0.5em;"),
                    ), css_class="row", style='padding-top:1em;'

                )
            ),

        )

    class Meta:
        model = DegreeType
        fields = [
            'is_in_use',
            'id',
            'display_order',
            'short_label',
            'long_label',
            'ROF_code'
        ]
