from django.test import TestCase
from .forms import DisabledInstituteYearForm, DircompInstituteYearForm, \
    DircompUniversityYearForm, UniversityYearForm, InstituteYearForm


class YearFormsTest(TestCase):
    def test_disabled_institute_year(self):
        form_data = {
            'date_expected_MECC': '12-05-2015',
            'date_last_notif': '07-05-2015',
        }
        form = DisabledInstituteYearForm(data=form_data)
        self.assertTrue(form.is_valid)

    def test_dircomp_institute_year(self):
        form_data = {
            'date_expected_MECC': '12-05-2015',
            'date_last_notif': '07-05-2015',
        }
        form = DircompInstituteYearForm(data=form_data)
        self.assertTrue(form.is_valid)

    def test_dircomp_university_year(self):
        form_data = {
            'date_validation': '12-05-2015',
            'date_expected': '07-05-2015',
        }
        form = DircompUniversityYearForm(data=form_data)
        self.assertTrue(form.is_valid)

    def test_university_year(self):
        form_data = {
            'code_year': 2015,
            'label_year': 'Année universitaire 2015/2016',
            'is_target_year': False,
            'date_validation': '12-05-2015',
            'date_expected': '07-05-2015',
            'is_year_init': True,
            'pdf_doc': '',
        }
        form = UniversityYearForm(data=form_data)
        self.assertTrue(form.is_valid)

    def test_institute_year(self):
        form_data = {
            'date_validation': '12-05-2015',
            'date_expected': '07-05-2015',
        }
        form = InstituteYearForm(data=form_data)
        self.assertTrue(form.is_valid)
