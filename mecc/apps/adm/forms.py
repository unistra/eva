from .models import MeccUser
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,  Field
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User


class MeccUserForm(ModelForm):
    """
    Form for custom users with status, institute(cmp) and birth_date
    """
    def __init__(self, *args, **kwargs):
        super(MeccUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('status'),
            Field('birth_date'),
        )

    class Meta:
        model = MeccUser
        fields = ['status', 'cmp', 'birth_date', ]


class UserForm(ModelForm):
    """
    Form for basic user
    """
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.Layout = Layout(
            Field('username'),
            Field('last_name'),
            Field('first_name'),
            Field('email'),
        )

    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'email']
