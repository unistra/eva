from django.test import TestCase
from .forms import ECIForm


class ECIFormTest(TestCase):
    def test_form(self):
        form_data = {
            'member_type': 'TEST1',
            'username': 'user',
            'last_name': 'name',
            'first_name': 'firstname'
        }
        form = ECIForm(data=form_data)
        self.assertFalse(form.is_valid())
