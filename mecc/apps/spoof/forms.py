from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button, Div, Field
from crispy_forms.bootstrap import FormActions
from django.contrib.auth.models import User


class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('username'),
            Field('password'),
        )

    class Meta:
        model = User
        fields = ['username', 'password']
