from django import forms
from .models import StructureObject, ObjectsLink, Exam
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Div
from django.utils.translation import ugettext as _


class StructureObjectForm(forms.ModelForm):

    regime = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(('E', _('ECI')), ('C', _('CC/CT'))),
        label=_('Régime'), initial='E',
    )
    period = forms.ChoiceField(
        widget=forms.RadioSelect,
        initial='I',
        choices=[
            ('I', _("Semestre impair")),
            ('P', _("Semestre pair")),
            ('A', _("Année")),
        ], label=_("Période")
    )
    session = forms.ChoiceField(
        widget=forms.RadioSelect,
        initial='1',
        choices=[
            ('1', _('Session unique')),
            ('2', _('2 sessions')),
        ], label=_("Sessions")
    )

    def __init__(self, *args, **kwargs):
        super(StructureObjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Div(
                    'nature',
                    'is_in_use',
                    css_class="x"
                ),
                'label',
                Div(
                    'RESPENS_id',
                    'ECTS_credit',
                    css_class="y"
                ),
                Div(
                    'period',
                    'regime',
                    'session',
                    css_class="centerme"
                ),
                Div(
                    'mutual',
                    HTML("""
<a id="preview-consumer" href="#" onclick='preview-consumer()' >Voir les consommateur </a>
                    """),
                    css_class='y mutual'
                ),
                css_class="item-70 padding-1 structure-form-left dir-row"
            ),
            Div(
                Div(
                    'ref_si_scol',
                    css_class="boxed padding-1"
                ),
                Div(
                    'ROF_ref',
                    Div(
                        'ROF_code_year',
                        'ROF_nature',
                        'ROF_supply_program',
                        css_class="disabled disabled-event"
                    ),
                    css_class="boxed padding-1"
                ),
                css_class="item-30  padding-1"
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
