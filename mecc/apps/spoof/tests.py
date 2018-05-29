from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from .views import home
from django.contrib.sessions.middleware import SessionMiddleware


def add_session_to_request(request):
    """
    Pdf views needs sessions
    """
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()


class SpoofTest(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1")
        self.u2 = User.objects.create_user(username="u2")
        self.u3 = User.objects.create_user(username="u3")
        self.des3 = Group.objects.create(name='DES3')
        self.u1.groups.add(self.des3)
        self.factory = RequestFactory()

    def test_home(self):
        request = self.factory.get('/spoof')
        add_session_to_request(request)
        request.user = self.u2
        resp = home(request)
        self.assertEqual(resp.status_code, 403)
        request.user = self.u1
        resp = home(request)
        self.assertEqual(resp.status_code, 200)
        request.session['is_spoofed_user'] = False
        resp = home(request)
        self.assertEqual(resp.status_code, 200)
    #
    # def test_spoof_id(self):
    #     req = self.factory.post(
    #         '/spoof/spoof',
    #         {'asked_username': 'u2', 'pass': '123456'},
    #         HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    #     )
    #     add_session_to_request(req)
    #     req.user = self.u1
    #     req.session['real_username'] = "u2"
    #     req.session['BACKEND_SESSION_KEY'] = BACKEND_SESSION_KEY
    #     resp = spoof_user(req)
    #     self.assertEqual(resp.status_code, 200)
    #     request = self.factory.post(
    #         '/spoof',
    #         {'asked_username': 'test',
    #          'pass': "123456"},
    #         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
