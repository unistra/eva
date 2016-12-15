from django import forms

from .models import Rule, Paragraph
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Field, Div, Submit
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from ckeditor.widgets import CKEditorWidget


class ParagraphForm(forms.ModelForm):
    """
    Paragraph form
    """
    display_order = forms.IntegerField(
        initial=0, label=_("N° Affichage"), required=False)

    text_standard = forms.CharField(widget=CKEditorWidget(), label=_("Texte de \
        l'alinéa standard <span class=required-fields style=color:#004A87\
        >Champ obligatoire</span>"), required=False)

    text_derog = forms.CharField(widget=CKEditorWidget(), label=_("Texte de \
        consigne pour la saisie de l'alinéa dérogatoire"),
                                 required=False)

    text_motiv = forms.CharField(widget=CKEditorWidget(), label=_("Texte de \
        consigne pour la saisie des motivations"), required=False)

    is_interaction = forms.BooleanField(required=False, label=_('Dérogation \
        possible'))

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
                        'is_interaction',
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
                css_class="paddin-top disabled-event ", id="text_derog"
            ),
            Div(
                Div(
                    'text_motiv',
                    css_class=" item-70 item disabled-event", id="text_motiv"
                ),
                Div(
                    Submit(
                        'add', _('Valider et retourner à la règle'),
                        onclick="_isEdited=false;",
                        css_class="form-submit-paraph-item btn-lines",
                        style=""),
                    HTML("""
                <a class='btn form-submit-paraph-item btn-default btn-lines'
                href={% url 'rules:rule_edit' id=rule.id%} >
                Annuler et retourner à la règle </a>
                         """),
                    css_class='item-30'
                ),
                css_class='parent '
            )
        )

    def clean(self):
        # if self.cleaned_data.get('is_cmp') is False:
        #     raise ValidationError(_("Veuillez selectionner un régime."))

        return self.cleaned_data

    class Meta:
        model = Paragraph
        fields = [
            'display_order',
            'is_in_use',
            # 'is_cmp',
            'is_interaction',
            'text_standard',
            'text_derog',
            'text_motiv',
        ]


class AddDegreeTypeToRule(forms.ModelForm):
    """
    Form for adding degreetype to rule
    """

    class Meta:
        model = Rule
        fields = ['degree_type']


class RuleForm(forms.ModelForm):
    """
    Rule form
    """
    EDITED_CHOICES = (
        ('X', _('Nouvelle')),
        ('O', _('Oui')),
        ('N', _('Non')),
    )

    is_edited = forms.ChoiceField(choices=EDITED_CHOICES,
                                  label=_("La règle a-t-elle été modifiée ?"),
                                  required=False)

    label = forms.CharField(
        label=('Libellé de règle'),
        widget=forms.TextInput(attrs={'placeholder': _(
            'Saisir ici le libellé de la nouvelle règle')}))

    display_order = forms.IntegerField(
        initial=0, label=_("N° d'ordre d'affichage"))

    def __init__(self, *args, **kwargs):
        super(RuleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'

        self.helper.layout = Layout(
            Div(
                HTML("""
            <div class="item item-3 grey-font">
              <label class="">ID règle <small>(auto)</small> : </label>
              <span id="rule_id"> {{latest_id | stringformat:"05d"}}</span>
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
                          <label class="">Régime(s) concerné(s)<span class="asteriskField">*</span> : </label>
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
                HTML('<span class="required-fields blue" style="margin-top:1em;">\
                *Champ obligatoire</span>'),
                Div(
                    FormActions(
                        Submit('add', _('Valider'), css_class="btn-xs",
                               onclick="_isEdited=false"),
                    ), css_class='on-right',
                ),
                css_class='parent last-line'
            ),
        )

    def clean(self):
        if (self.cleaned_data.get(
                'is_ccct') or self.cleaned_data.get('is_eci')) is False:
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
