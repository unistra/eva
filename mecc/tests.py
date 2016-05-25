from django.test import TestCase
from mecc.apps.years.models import UniversityYear
from django.db.models import Q


class MeccTestView(TestCase):

    def setUp(self):
        self.university_year1 = UniversityYear.objects.create(
            code_year=2014, is_target_year=True)
        self.university_year2 = UniversityYear.objects.create(
            code_year=2015, is_target_year=False)

    def test_get_current_year(self):
        self.current_year = list(UniversityYear.objects.filter(
            Q(is_target_year=True))).pop(0)
        self.assertNotEqual(
            self.current_year.code_year, self.university_year2.code_year)
        self.assertEqual(
            self.current_year.code_year, self.university_year1.code_year)
