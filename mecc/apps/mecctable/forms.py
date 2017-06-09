from django import forms
from .models import StructureObject, ObjectsLink, Exam
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Div, Field
from django.utils.translation import ugettext as _
# from django.core import management

# def setup():
#     management.call_command('loaddata', 'fixtures/tests.json', verbosity=1)
#
#
# def teardown():
#         management.call_command('flush', verbosity=0, interactive=False)
#


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
            ('2', _('2 sessions')),
            ('1', _('Session unique')),
        ], label=_("Sessions")
    )

    external_name = forms.CharField(label=" ")

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
                    Div(

                        HTML(
                            """
<div id="div_id_RESPENS_id" class="form-group">
    <label for="id_RESPENS_id" class="control-label ">
        Responsable d'enseignement
    </label>
    <div class="controls input-group ">
         <input class="textinput textInput form-control" id="id_RESPENS_id"
         name="RESPENS_id" placeholder="Rechercher un enseignant"
         readonly="" data-target="" type="text" style="display:none">
         <input class="textinput textInput form-control" id="name_respens"
         name="name_respens" placeholder="Rechercher un enseignant"
         readonly="" data-target="" type="text">
         <span class="input-group-addon" id="basic-addon2">
            <span data-toggle="modal" data-target="#searchMember"
            class="select glyphicon glyphicon-search" id="go-respens"></span>
         </span>
    </div>
</div>
                            """
                        ),

                        Field(
                            'external_name',
                            placeholder="Saisir un intervenant extérieur"
                        ),
                        css_class="y"
                    ),
                    'ECTS_credit',
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
<a id="preview-consumer" href="#"  >
Voir les consommateurs </a>
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
            'external_name'
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
