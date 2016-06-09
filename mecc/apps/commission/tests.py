from django.test import TestCase, RequestFactory, TransactionTestCase
from .forms import ECIForm
from .models import ECICommissionMember
from .views import home, change_typemember, send_mail
from ..adm.models import Profile, MeccUser
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# from django.core.urlresolvers import reverse


def create_ajax_request():
    return RequestFactory.get(
        '/pdf', {'student_number': '21214045'},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')


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


class ECIMemberTest(TestCase):

    def setUp(self):
        Profile.objects.create(code='ECI', label="Membre de la commission ECI")
        Profile.objects.create(code='DIRCOMP', label="Directeur de composante")
        User.objects.create_user(username="TEST1")
        ECICommissionMember.objects.create(username="TEST3")
        ECICommissionMember.objects.create(username="TEST2")

    def test_member(self):
        eci_member = ECICommissionMember.objects.get(username="TEST3")
        u = User.objects.get(username="TEST3")
        self.assertTrue(
            Profile.objects.get(code="ECI") in MeccUser.objects.get(
                user=u).profile.all())
        self.assertRaises(
            ValidationError,
            ECICommissionMember(username="TEST3").clean_fields)
        self.assertEqual(
            str(eci_member),
            "%s %s" % (eci_member.last_name, eci_member.first_name))

    def test_remove_member(self):
        eci_member1 = ECICommissionMember.objects.get(username="TEST3")
        u1 = User.objects.get(username="TEST3")
        mecc_u1 = MeccUser.objects.get(user=u1)
        mecc_u1.profile.add(Profile.objects.get(code="DIRCOMP"))
        eci_member1.delete()
        eci_member2 = ECICommissionMember.objects.get(username="TEST2")
        eci_member2.delete()

        self.assertFalse(
            Profile.objects.get(code="ECI") in mecc_u1.profile.all())
        self.assertTrue(
            "TEST2" not in [e.username for e in User.objects.all()]
        )

#
# class CommissionViewTest(TestCase):
#
#     def test_send_mail(self):
#
#         request = self.factory.post(
#             '/commission/send_mail',
#             {'subject': '[MECC]', 'body': "Hello",
#              "from_email": "from@mail.xy", "to": "to@mail.xy",
#              "cc": "cc@mail.xy", "bcc": "bcc@mail.xy"},
#             HTTP_X_REQUESTED_WITH='XMLHttpRequest')
#
#         resp = send_mail(request)
#
#         self.assertEqual(resp.status_code, 200)


# TransactionTestCase allow to not raise TransactionManagementError
class CommissionTrajsitionViewTest(TransactionTestCase):

    def setUp(self):
        Profile.objects.create(code='ECI', label="Membre de la commission ECI")
        self.factory = RequestFactory()

    def test_home(self):
        request = RequestFactory().get('/fake-path')
        u = User.objects.create_user(username='test')
        request.user = u
        resp = home(request)
        self.assertEqual(resp.status_code, 200)

        request = RequestFactory().post('/fake-path')

        changes = [
            ('email', 'fake@unistra.fr'),
            ('member_type', 'commission'),
            ('last_name', 'DOE'),
            ('first_name', 'John'),
            ('username', 'johndoe'),
            ('add', 'Ajouter'),
        ]

        for field, value in changes:
            form_data = {}
            form_data[field] = value

    def test_changetypemember(self):
        u = ECICommissionMember.objects.create(
            username="johndoe", member_type="tenured", email="jd@nope.eu")

        request = self.factory.post(
            '/commission/change_typemember',
            {'username': 'johndoe', 'type_member': "supply"},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        request.user = User.objects.get(username="johndoe")

        self.assertEqual(
            u.member_type,
            'tenured')

        resp = change_typemember(request)

        self.assertEqual(
            ECICommissionMember.objects.get(username="johndoe").member_type,
            'supply')

        self.assertEqual(resp.status_code, 200)

    def test_send_mail(self):

        request = self.factory.post(
            '/commission/send_mail',
            {'subject': '[MECC]', 'body': "Hello",
             "from_email": "from@mail.xy", "to": "to@mail.xy",
             "cc": "cc@mail.xy", "bcc": "bcc@mail.xy"},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        u = User.objects.create_user(username='test')
        request.user = u
        resp = send_mail(request)
        self.assertEqual(resp.status_code, 302)
