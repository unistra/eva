from django.test import TestCase, RequestFactory
from mecc.apps.years.models import UniversityYear
from django.db.models import Q
from mecc.middleware import UsefullDisplay
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User


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

    def test_middlware(self):
        self.factory = RequestFactory()
        request = self.factory.get('/spoof')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = u = User.objects.create_user(username='test')
        middleware = UsefullDisplay().process_request(request)
        self.assertEqual(request.display.get('user'), u)
