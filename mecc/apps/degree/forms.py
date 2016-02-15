from django import forms
from .models import DegreeType
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button, Div, Field, \
    HTML
from crispy_forms.bootstrap import InlineField

from django.utils.translation import ugettext_lazy as _


class DegreeTypeForm(forms.ModelForm):
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
                        Div(
                            HTML("""
                                <label for="id_degree_type" class="control-label col-md-5">
                                ID type diplôme <small>(auto)</small></label>
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
                        Div(Field('mecc_cat', readonly=True), css_class='col-md-12'),
                        css_class="row"
                    ),
                ),
                css_class='modal-body'

            ),

        )

    class Meta:
        model = DegreeType
        fields = ['is_in_use', 'id', 'display_order', 'short_label',
                  'long_label', 'mecc_cat']
