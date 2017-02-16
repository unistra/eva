from django import forms
from .models import StructureObject, ObjectsLink, Exam
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Field, Div, Submit
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from crispy_forms.bootstrap import InlineField, FormActions


class StructureObjectForm(forms.ModelForm):

    regime = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(('E', _('ECI')), ('C', _('CC/CT'))),
        label=_('Régime'), initial='E',
    )
    period = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[
            ('I', _("Semestre impair")),
            ('P', _("Semestre pair")),
            ('A', _("Année")),
        ], label=_("Période")
    )
    session = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[
            ('I', _("Semestre impair")),
            ('P', _("Semestre pair")),
            ('A', _("Année")),
        ], label=_("Sessions")
    )

    def __init__(self, *args, **kwargs):
        super(StructureObjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-5'
        self.helper.field_class = 'col-lg-7'
        self.helper.layout = Layout(
            Div(
                'nature',
                'is_in_use',
                'label',
                'RESPENS_id',
                'ECTS_credit',
                Div(
                    'period',
                    'regime',
                    'session',
                    css_class="boxed"
                ),
                'mutual',
                css_class="item-70"
            ),
            Div(
                Div(
                    'ref_si_scol',
                    css_class="boxed"
                ),
                Div(
                    'ROF_ref',
                    'ROF_code_year',
                    'ROF_nature',
                    'ROF_supply_program',
                    css_class="boxed"
                ),
                css_class="item-30"
            )

        )

    class Meta:
        model = StructureObject
        fields = [
            'nature',
            'is_in_use',
            'label',
            'RESPENS_id',
            'ECTS_credit',
            'period',
            'regime',
            'session',
            'mutual',
            'ref_si_scol',
            'ROF_ref',
            'ROF_code_year',
            'ROF_nature',
            'ROF_supply_program',
        ]


class ObjectsLinkForm(forms.ModelForm):

    class Meta:
        model = ObjectsLink
        fields = ['code_year', 'id_parent', 'id_child', 'order_in_child']


class ExamForm(forms.ModelForm):

    class Meta:
        model = Exam
        fields = [
            'code_year', 'id_attached', 'session', 'regime', 'label',
            'additionnal_info', 'exam_duration_m',
            'convocation', 'is_session_2', 'threshold_session_2'
        ]
#
#
# class RuleForm(forms.ModelForm):
#     """
#     Rule form
#     """
#     EDITED_CHOICES = (
#         ('X', _('Nouvelle')),
#         ('O', _('Oui')),
#         ('N', _('Non')),
#     )
#
#     is_edited = forms.ChoiceField(choices=EDITED_CHOICES,
#                                   label=_("La règle a-t-elle été modifiée ?"),
#                                   required=False)
#
#     label = forms.CharField(
#         label=('Libellé de règle'),
#         widget=forms.TextInput(attrs={'placeholder': _(
#             'Saisir ici le libellé de la nouvelle règle')}))
#
#     display_order = forms.IntegerField(
#         initial=0, label=_("N° d'ordre d'affichage"))
#
#     def __init__(self, *args, **kwargs):
#         super(RuleForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_tag = False
#         self.helper.form_class = 'form-horizontal'
#
#         self.helper.layout = Layout(
#             Div(
#                 HTML("""
#             <div class="item item-3 grey-font">
#               <label class="">ID règle <small>(auto)</small> : </label>
#               <span id="rule_id"> {{latest_id | stringformat:"05d"}}</span>
#             </div>
#             <div class="item item-3 grey-font">
#               <label class="">Année universitaire :</label>
#               <span id="rule_date"> {{current_year}} </span>
#             </div>
#                 """),
#                 Div(
#
#                     'is_in_use',
#                     css_class='item'
#                 ),
#                 css_class='parent'
#             ),
#             Div(
#                 Div(
#                     'label',
#                     css_class='item-100'
#                 ),
#                 css_class='parent'
#             ),
#             Div(
#                 Div(
#
#                     HTML("""
#                           <label class="">Régime(s) concerné(s)<span class="asteriskField">*</span> : </label>
#                     """),
#                     Div(
#                         'is_eci',
#                         css_class='item item-concerned'
#                     ),
#                     Div(
#                         'is_ccct',
#                         css_class='item item-concerned'
#                     ),
#                     css_class='div_is_concerned'
#                 ),
#                 css_class='parent'
#             ),
#             Div(
#                 Field('display_order'),
#                 'is_edited',
#                 HTML('<span class="required-fields blue" style="margin-top:1em;">\
#                 *Champ obligatoire</span>'),
#                 Div(
#                     FormActions(
#                         Submit('add', _('Valider'), css_class="btn-xs",
#                                onclick="_isEdited=false"),
#                     ), css_class='on-right',
#                 ),
#                 css_class='parent last-line'
#             ),
#         )
#
#     def clean(self):
#         if (self.cleaned_data.get(
#                 'is_ccct') or self.cleaned_data.get('is_eci')) is False:
#             raise ValidationError(_("Veuillez selectionner un régime."))
#
#         return self.cleaned_data
#
#     class Meta:
#         model = Rule
#         fields = [
#             'is_in_use',
#             'label',
#             'is_eci',
#             'is_ccct',
#             'display_order',
#             'is_edited',
#         ]
