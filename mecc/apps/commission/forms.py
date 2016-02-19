from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button, Div, Field
from crispy_forms.bootstrap import FormActions
from django.utils.translation import ugettext_lazy as _

from .models import ECICommissionMember
from ..adm.models import MeccUser
from django.contrib.auth.models import User


class ECIForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ECIForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('username'),
            Field('last_name'),
            Field('first_name'),
            Field('member_type'),
            Field('mail')
        )

    class Meta:
        model = ECICommissionMember
        fields = ['username', 'member_type', 'last_name', 'first_name', 'email']

#
# class MeccUserForm(ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(MeccUserForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_tag = False
#         self.helper.layout = Layout(
#             Field('status'),
#             # Field('birth_date'),
#         )
#
#     class Meta:
#         model = MeccUser
#         fields = ['status', 'cmp', 'birth_date', ]
#
#
# class UserForm(ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(UserForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_tag = False
#         self.helper.Layout = Layout(
#             Field('username'),
#             Field('last_name'),
#             Field('first_name'),
#             Field('email'),
#         )
#
#     class Meta:
#         model = User
#         fields = ['username', 'last_name', 'first_name', 'email']


# class ECIForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(ECIForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#
#             Div(
#                 Div(Field('last_name', readonly=True), css_class='col-xs-4'),
#                 Div(Field('first_name', readonly=True), css_class='col-xs-4'),
#                 Div(Field('status', readonly=True), css_class='col-xs-4'),
#                 css_class='row'),
#
#             Div(
#                 Div(Field('institute', readonly=True), css_class='col-xs-4'),
#                 Div(Field('mail', readonly=True), css_class='col-xs-4'),
#                 Div(Field('id_member', readonly=True), css_class='col-xs-4'),
#                 css_class='row'),
#
#             Div(
#                 Div('member_type', css_class='col-xs-12'),
#                 css_class='row'),
#
#         )
#
#     class Meta:
#         model = ECICommissionMember
#         exclude = ()
