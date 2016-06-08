from django.test import TestCase
from mecc.apps.degree.forms import DegreeTypeForm, DegreeForm


class DegreeTypeFormTest(TestCase):

    def test_form(self):
        form_data = {'label': 'TEST1'}
        form = DegreeTypeForm(data=form_data)
        self.assertFalse(form.is_valid())


class DegreeFormTest(TestCase):

    def test_form(self):
        form_data = {'short_label': 'TEST1'}
        form = DegreeForm(data=form_data)
        self.assertFalse(form.is_valid())
