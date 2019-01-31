from ckeditor.widgets import CKEditorWidget
from crispy_forms.bootstrap import StrictButton, Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Div, Submit
from django import forms
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from mecc.apps.training.models import Training, SpecificParagraph, AdditionalParagraph
from mecc.apps.rules.models import Rule
from mecc.apps.institute.models import Institute


class AdditionalParagraphForm(forms.ModelForm):
    """
    Additional paragraph form
    """
    text_additional_paragraph = forms.CharField(
        widget=CKEditorWidget(), label='', required=True)

    def __init__(self, *args, **kwargs):
        super(AdditionalParagraphForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            HTML("{{additional}}"),
            'text_additional_paragraph',
        )

    class Meta:
        model = AdditionalParagraph
        fields = [
            'text_additional_paragraph'
        ]

class SpecificParagraphDerogForm(forms.ModelForm):
    """
    Specific paragraph form
    """
    text_specific_paragraph = forms.CharField(
        widget=CKEditorWidget(), label='', required=True)
    text_motiv = forms.CharField(
        widget=CKEditorWidget(), label='', required=True)

    def __init__(self, *args, **kwargs):
        super(SpecificParagraphDerogForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            HTML("<b>ETAPE 1 :</b>{{text_derog|safe}}"),
            'text_specific_paragraph',
            HTML("<b>ETAPE 2 :</b>{{text_motiv|safe}}"),
            'text_motiv',
        )

    class Meta:
        model = SpecificParagraph
        fields = [
            'text_specific_paragraph',
            'text_motiv'
        ]

    def clean(self):
        if self.cleaned_data.get('text_specific_paragraph') in ['', ' ', None]:
            raise ValidationError(_("Veuillez remplir le texte de dérogation"))
        if self.cleaned_data.get('text_motiv') in ['', ' ', None]:
            raise ValidationError(_("Veuillez remplir le texte de motivation"))

        return self.cleaned_data

class ExtraTrainingsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        training = kwargs.pop('training')
        rule = kwargs.pop('rule')
        specific = kwargs.pop('specific', None)
        additional = kwargs.pop('additional', None)
        super(ExtraTrainingsForm, self).__init__(*args, **kwargs)

        trainings = Training.objects.\
            filter(
                code_year=training.code_year,
                supply_cmp=training.supply_cmp,
                degree_type__in=rule.degree_type.all(),
                progress_rule="E").\
            filter(
                Q(date_val_cmp__isnull=True) \
                | \
                Q(date_val_cmp__isnull=False, date_res_des__isnull=False)).\
            exclude(
                id=training.id).\
            order_by(
                'degree_type',
                'label'
            )

        if rule.is_eci and not rule.is_ccct:
            trainings = trainings.filter(MECC_type='E')
        elif rule.is_ccct and not rule.is_eci:
            trainings = trainings.filter(MECC_type='C')

        mode = ""
        if specific:
            mode = "cette dérogation"
            same_specific_training_ids = [
                specific.training_id\
                for specific\
                in SpecificParagraph.objects.filter(
                    code_year=specific.code_year,
                    rule_gen_id=specific.rule_gen_id,
                    paragraph_gen_id=specific.paragraph_gen_id
                )
            ]
            trainings = trainings.exclude(
                id__in=same_specific_training_ids
            )
        else:
            mode = "cet alinéa additionel"
            same_additional_training_ids = [
                additional.training_id\
                for additional\
                in AdditionalParagraph.objects.filter(
                    code_year=additional.code_year,
                    rule_gen_id=additional.rule_gen_id,
                )
            ]
            trainings = trainings.exclude(
                id__in=same_additional_training_ids
            )

        self.fields['extra_trainings'] = forms.MultipleChoiceField(
            choices=((training.id, training.label) for training in trainings),
            widget=forms.CheckboxSelectMultiple(),
            required=False,
            label="Sélectionner les formations" if trainings.exists() else "Vous ne pouvez pas appliquer {} à d'autres formations.".format(mode)
        )

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            HTML("<b>ETAPE 3 :</b>"),
            'extra_trainings'
        )

class RespTrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = [
            'resp_formations'
        ]


class ValidationTrainingForm(forms.ModelForm):
    """
    Training form with validation
    """
    def __init__(self, *args, **kwargs):
        super(ValidationTrainingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                'progress_rule',
                'progress_table',
                'date_val_cmp',
                'date_res_des',
                'date_visa_des',
                'date_val_cfvu',

                css_class="training-form training-form-1",
            )
        )

    class Meta:
        model = Training
        fields = [
            'progress_rule',
            'progress_table',
            'date_val_cmp',
            'date_res_des',
            'date_visa_des',
            'date_val_cfvu',
            'institutes',
            'supply_cmp',
        ]


class TrainingForm(forms.ModelForm):
    """
    Training form
    """

    def clean(self):
        if self.cleaned_data.get('institutes') is None:
            raise ValidationError(("Veuillez selectionner \
moins une composante."))
        available_institues = self.cleaned_data.get('institutes').all()
        available_code = [e.code for e in available_institues]
        if self.cleaned_data.get('supply_cmp') not in available_code:
            raise ValidationError(("Veuillez selectionner au \
moins une composante porteuse."))

        return self.cleaned_data

    MECC_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(('E', _('ECI')), ('C', _('CC/CT'))),
        label=_('Régime'), initial='E',
        required=False
    )
    session_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(('2', _('2 sessions')), (('1', _('Session unique')))),
        label=_('Session'), initial='2', required=False

    )
    label = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'style': 'resize:none;'}),
        label=_("Intitulé de la formation"),
        help_text=_("Année/parcours")
    )

    def __init__(self, *args, **kwargs):
        super(TrainingForm, self).__init__(*args, **kwargs)
        if self.instance.label not in ["", '', None]:
            self.fields['degree_type'].widget.attrs['disabled'] = \
                self.fields['label'].widget.attrs['disabled'] = \
                self.fields['is_used'].widget.attrs['disabled'] = \
                self.fields['ref_cpa_rof'].widget.attrs['disabled'] = \
                True if Institute.objects.get(code=self.instance.supply_cmp).ROF_support else False
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                'degree_type',
                Div(
                    'label',
                    Div(
                        'is_used',
                        'MECC_tab',
                    ),
                ),
                Div(
                    HTML("""
                        <div id="ultra_small"></div>
                        """),
                    Div(
                        'MECC_type',
                        'session_type',
                        HTML("""
                        <div class="re-apply">
                        {% if not new %}
                            {% if training.has_custom_paragraph or training.has_exam %}
                            <button type="button" class="btn btn-primary" name="transform">Transformer</button>
                            <br /><br />
                            <button type="reset" class="btn btn-primary" name="reset" onclick="_isEdited=false;" style="width: 100%;">Annuler</button>
                            {% include "training/modals/training_transform.html" %}
                            {% else %}
                            <button type="button" class="btn btn-primary " name="reapply">Réappliquer <br/> aux objets</button>
                            {% endif %}
                        {% endif %}
                        </div>
                        """),
                        Div(
                            HTML("""
                                <label> &nbsp;</label>
                                """),
                            Div(
                                'ref_cpa_rof',
                                'ref_si_scol',
                                css_class='controls'
                            ),
                            css_class="form-group aaaa"
                        ),
                        css_class="form-add-stats",
                        css_id="regime-session",
                    )
                ),
                Div('institutes', css_class="hidden"),
                Div('supply_cmp', css_class="hidden"),
            ),
        )

    class Meta:
        model = Training
        fields = [
            'degree_type',
            'is_used',
            'MECC_tab',
            'label',
            'MECC_type',
            'session_type',
            'ref_cpa_rof',
            'ref_si_scol',
            'institutes',
            'supply_cmp',
        ]

class TrainingTransformForm(forms.ModelForm):
    MECC_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(('E', _('ECI')), ('C', _('CC/CT'))),
        label=_('Régime'),
        initial='E',
        required=False
    )
    session_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(('2', _('2 sessions')), (('1', _('Session unique')))),
        label=_('Session'),
        initial='2',
        required=False
    )
    def __init__(self, *args, **kwargs):
        super(TrainingTransformForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Div(
                'MECC_type',
                'session_type',
                css_class="form-add-stats",
            )
        )

    class Meta:
        model = Training
        fields = [
            'MECC_type',
            'session_type',
        ]
