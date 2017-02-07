from django import forms
from .models import StructureObject, ObjectsLink, Exam


class StructureObjectForm(forms.ModelForm):

    class Meta:
        model = StructureObject
        fields = ['label', 'is_in_use', 'period', 'RESPENS_id',
                  'ROF_ref', 'ROF_code_year', 'ROF_nature', 'ref_si_scol']


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
