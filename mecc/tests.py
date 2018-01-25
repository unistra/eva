from django.test import TestCase, RequestFactory
from mecc.apps.years.models import UniversityYear
from django.db.models import Q
from mecc.middleware import UsefullDisplay
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from django.template import Context, Template


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


class MeccTestTemplateTags(TestCase):

    def setUp(self):
        self.obj = UniversityYear.objects.create(
            code_year=1984, is_target_year=True)

    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def testRedifyTemplateTag(self):
        rendered = self.render_template(
            '{% load mecc_tags %}'
            '{{ "1984" | redify:"1984" }}'
        )
        self.assertEqual(
            rendered, "&lt;span class=&quot;red&quot;&gt;1984&lt;/span&gt;")

        rendered = self.render_template(
            '{% load mecc_tags %}'
            '{{ "1984" | redify:"2048" }}'
        )

        self.assertEqual(rendered, "1984")

    def testRedOrGreenifyTemplateTag(self):
        rendered = self.render_template(
            '{% load mecc_tags %}'
            '{{ "1984" | redorgreenify:"1984" }}'
        )
        self.assertEqual(
            rendered, "&lt;span class=&quot;green&quot;&gt;1984&lt;/span&gt;")

        rendered = self.render_template(
            '{% load mecc_tags %}'
            '{{ "1984" | redorgreenify:"2048" }}'
        )

        self.assertEqual(rendered, "&lt;span class=&quot;red&quot;&gt;1984&lt;/span&gt;")

    def testGetBootstrapAlertMsgCssName(self):
        rendered = self.render_template(
            '{% load mecc_tags %}'
            '{% get_bootstrap_alert_msg_css_name "error" as alert_tag %}'
            '{{ alert_tag }}'
        )

        self.assertEqual(rendered, "danger")

        rendered = self.render_template(
            '{% load mecc_tags %}'
            '{% get_bootstrap_alert_msg_css_name "lol" as alert_tag %}'
            '{{ alert_tag }}'
        )

        self.assertEqual(rendered, "lol")
