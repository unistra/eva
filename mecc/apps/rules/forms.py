from django import forms
from django.forms import ModelForm

from .models import Rule, Paragraph, Impact
from crispy_forms.bootstrap import InlineCheckboxes, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Field, Div, Fieldset, Button, Submit
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE

class ParagraphForm(forms.ModelForm):

    display_order = forms.IntegerField(initial=0, label=_("N° Affichage"))

    text_standard = forms.CharField(widget=TinyMCE(), label=_("Texte de l'alinéa standard"))

    text_derog = forms.CharField(widget=TinyMCE(), label=_("Texte de \
        consigne pour la saisie de l'alinéa dérogatoire (ou de composante)"))

    text_motiv = forms.CharField(widget=TinyMCE(), label=_("Texte de consigne \
        pour la saisie des motivations"))

    impact = forms.ChoiceField(
        choices=((e.code, e.description) for e in Impact.objects.all()),
        label=_('Impact TM'))

    def __init__(self, *args, **kwargs):
        super(ParagraphForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("""
                        <div class="grey-font item flex-start">
                          <label class="">ID alinéa <small>(auto)</small> : </label>
                          <span id="rule_id"> {{id_paragraph}}</span>
                        </div>
                    """),
                    Div(

                        'display_order',
                        css_class="item disp flex-start"
                    ),
                    Div(
                        'is_in_use',
                        css_class="item aligned-left flex-start"
                    ),
                    Div(
                        'is_cmp',
                        Div(
                            Div('is_interaction', css_class="is_interaction"),
                            Field('impact', css_class="item flex-end"),
                            css_class="parent"
                        ),
                        css_class="item item-35 paraph-cmp",
                    ),

                    css_class="parent"
                ),

                css_class="has-bottom-border"
            ),
            Div(
                'text_standard',
                css_class="paddin-top"
            ),
            Div(
                'text_derog',
                css_class="paddin-top"
            ),
            Div(
                Div(
                    'text_motiv',
                    css_class=" item-70 item"
                ),
                Div(
                    FormActions(
                        Div(

                        Submit(
                            'add', _('Valider et retourner à la règle'),
                            css_class="form-submit-paraph-item btn-lines",
                            style=""),
                        Button(
                            'cancel', ('Annuler et retourner à la règle'),
                            onclick='history.go(-1);',
                            css_class='form-submit-paraph-item  btn-lines'),
                        )
                    ),
                    css_class='item item-30 flex-center'
                ),
                css_class='parent paddin-top'
            )
        )


    class Meta:
        model = Paragraph
        fields =[
            'display_order',
            'is_in_use',
            'is_cmp',
            'is_interaction',
            'impact',
            'text_standard',
            'text_derog',
            'text_motiv',
        ]

class AddDegreeTypeToRule(forms.ModelForm):
    class Meta:
        model = Rule
        fields = ['degree_type']

class RuleFormInit(forms.ModelForm):
    EDITED_CHOICES = (
        ('X', _('Nouvelle')),
        ('O', _('Oui')),
        ('N', _('Non')),
    )

    is_edited = forms.ChoiceField(choices=EDITED_CHOICES,
        label=_("La règle a-t-elle été modifiée ?"))

    label = forms.CharField(label=('Libellé de règle'),
        widget=forms.TextInput(attrs={'placeholder': _('Saisir ici le libellé de la nouvelle règle') }))


    display_order = forms.IntegerField(initial=0, label=_("N° d'ordre d'affichage"))

    def __init__(self, *args, **kwargs):
        super(RuleFormInit, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'

        self.helper.layout = Layout(
            Div(
                HTML("""
                    <div class="item item-3 grey-font">
                      <label class="">ID règle <small>(auto)</small> : </label>
                      <span id="rule_id"> {{latest_id}}</span>
                    </div>
                    <div class="item item-3 grey-font">
                      <label class="">Année universitaire :</label>
                      <span id="rule_date"> {{current_year}} </span>
                    </div>
                """),
                Div(


                'is_in_use',
                css_class='item'
                ),
                css_class='parent'
            ),
            Div(
                Div(
                'label',
                css_class='item-100'
                ),
                css_class='parent'
            ),
            Div(
                Div(

                    HTML("""
                          <label class="">Régime(s) concerné(s) : </label>
                    """),
                    Div(
                    'is_eci',
                    css_class='item item-concerned'
                    ),
                    Div(
                    'is_ccct',
                    css_class='item item-concerned'
                    ),
                    css_class='div_is_concerned'
                ),
                css_class='parent'
            ),
            Div(
                Field('display_order'),
                'is_edited',
                    Div(
                        FormActions(
                            Submit('add', _('Valider'),css_class="btn-xs",  onclick="_isEdited=false"),
                        ), css_class='on-right',
                    ),
                css_class='parent last-line'
            ),
        )

    def clean(self):
        if (self.cleaned_data.get('is_ccct') or self.cleaned_data.get('is_eci')) is False:
            raise ValidationError(_("Veuillez selectionner un régime."))

        return self.cleaned_data

    class Meta:
        model = Rule
        fields = [
            'is_in_use',
            'label',
            'is_eci',
            'is_ccct',
            'display_order',
            'is_edited',
        ]


class RuleFormInitOld(forms.ModelForm):
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
        self.helper.form_class = 'form-horizontal'

        self.helper.layout = Layout(
        Div(
            HTML("""
                <div class="col-xs-4 grey-font">
                  <label class="">ID règle <small>(auto)</small> : </label>
                  <span id="rule_id"> {{latest_id}}</span>
                </div>
                <div class="col-xs-5 grey-font">
                  <label class="">Année universitaire :</label>
                  <span id="rule_date"> {{current_year}} </span>
                </div>
            """),
            Div(
                Div(
                'is_in_use', css_class='pull-right col-xs-3'
                ),
            ),
            css_class="row"
        ),
        Div(
            Div(
                Field('label'),
                 css_class='col-xs-12'
            ),
            css_class='row'
        ),
        Div(
            Div(
                HTML("""
                <div class="col-xs-3 grey-font">
                  <label class="checkbox">Régime(s) concerné(s) : </label>
                </div>
                """),
                Div(
                    'is_eci',
                    css_class='col-xs-1'
                ),
                Div(
                    'is_ccct',
                    css_class='col-xs-1'
                ),
            ),
            css_class='row'
        ),
        Div(
            Div(
                'display_order',
                css_class='col-xs-3'
            ),
            Div(
                'is_edited' ,
                css_class='col-xs-6'
            ),
            css_class='row'
        ),
        )

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
