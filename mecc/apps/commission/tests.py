from django.test import TestCase
from .forms import ECIForm


class ECIFormTest(TestCase):
    def test_form(self):
        form_data = {'label': 'TEST1'}
        form = ECIForm(data=form_data)
        self.assertFalse(form.is_valid())
