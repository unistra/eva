from django import forms
from .models import DegreeType, Degree
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, Div, Field, \
    HTML
from crispy_forms.bootstrap import InlineField, FormActions

from django.utils.translation import ugettext as _


class DegreeForm(forms.ModelForm):
    """
    Degree form
    """
    label = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}), label=_("Intitulé réglementaire :"), help_text=_("(équivalent programme ROF)"))
    start_year = forms.CharField(label=_('Début'))
    end_year = forms.CharField(label=_('Fin'))
    ROF_code = forms.CharField(
        label=_("Références Programme ROF"),
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': _("[Identifiant programme ROF]") }
        )
    )
    APOGEE_code = forms.CharField(
        label=_("Références SI Scolarité"),
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': _("[Code APOGEE], saisie libre") }
        )
    )


    def __init__(self, *args, **kwargs):
        super(DegreeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        Div(
                            'degree_type',
                            'degree_type_label',
                            css_class='parent div-child-disp-flex label-child-w2'
                        ),
                        css_class="item-65",
                    ),
                    Div(
                        Div(

                        HTML("""
                           <a href="{% url 'degree:degree_create'  %}" class="btn btn-primary bottom-2em item" style="width:10em;margin-bottom:0.5em;">Créer un diplôme</a>
                        """),

                        Button('rof', _('[Référentiel OF]'), style="width:10em"),
                        css_class="flex-center dir-col",
                        style="self-align:flex-start",

                        ),
                        css_class='item-35 ',
                    ),

                    css_class="parent-centered degree-form-top"
                ),
                Div(
                    Div(
                        Div(
                            'label',
                            css_class='parent div-child-disp-flex label-child-w2'
                        ),
                        css_class="item-65",
                    ),
                    Div(
                        'is_used',
                        Div(
                            HTML("<div class='form-group' style='padding-right:1em;'><label>Validité :</label></div>"),
                            Div(

                                Field('start_year', style="display:inline"),
                                Field('end_year'),
                            style="width:65%",
                            css_class="div-child-disp-flex label-child-w2 dir-col"

                            ),
                            css_class="div-child-disp-flex disp-flex item-50",

                        ),
                        style="padding-left:2em;margin-top:-1em;",
                        css_class="item-35"
                    ),
                    css_class="has-bottom-border parent-centered degree-form-top"
                ),
                Div(
                    Div(

                        Div(
                            'ROF_code',
                            'APOGEE_code',
                        ),
                        css_class="item-35 border-right degree-form-left",
                        style="padding-top:2em;"
                    ),
                    Div('institutes', style="display:none"), #  TODO:Mettre le display en none
                    HTML(
                        """<div class='item-65' style="padding:2em 1em 1em 1em;">
                                 {% include "degree/add_cmp.html" %}
                        </div>
                        """
                    ),
                    css_class="parent disp-flex",


                ),
            css_class="has-bottom-border degree-form-bottom",
            ),
        Div(
            FormActions(
                Submit('add', _('Valider et fermer la fiche'), css_class=" btn btn-sm", style="width:30%", onclick="_isEdited=false"),
                HTML("""
                    <a style="width:30%" class="btn-primary btn btn-sm" href="{% url 'degree:list' filter='current' cmp='none'%}">Annuler et fermer la fiche</a>
                """),
            ),
            style="padding-top:1em;",
            css_class="buttons_list"
        )
        )

    class Meta:
        model = Degree
        fields = [
            'degree_type',
            'degree_type_label',
            'label',
            'is_used',
            'start_year',
            'end_year',
            'ROF_code',
            'APOGEE_code',
            'institutes'
        ]


class DegreeTypeForm(forms.ModelForm):
    """
    Degree type form
    """
    is_in_use = forms.BooleanField(required=False, initial=True,
        label=_("En service"),
    )

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
