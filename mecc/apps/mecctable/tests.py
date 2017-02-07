import unittest
from django.core.urlresolvers import reverse
from django.test import Client
from .models import StructureObject, ObjectsLink, Exam
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory
from mecc.apps.mecctable.views import StructureObjectListView


def create_django_contrib_auth_models_user(**kwargs):
    defaults = {}
    defaults["username"] = "username"
    defaults["email"] = "username@tempurl.com"
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


def create_django_contrib_auth_models_group(**kwargs):
    defaults = {}
    defaults["name"] = "group"
    defaults.update(**kwargs)
    return Group.objects.create(**defaults)


def create_django_contrib_contenttypes_models_contenttype(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ContentType.objects.create(**defaults)


def create_structureobject(**kwargs):
    defaults = {}
    defaults["label"] = "label"
    defaults["is_in_use"] = "is_in_use"
    defaults["period"] = "period"
    defaults["RESPENS_id"] = "RESPENS_id"
    defaults["ROF_ref"] = "ROF_ref"
    defaults["ROF_code_year"] = 2015
    defaults["ROF_nature"] = "ROF_nature"
    defaults["ref_si_scol"] = "ref_si_scol"
    defaults.update(**kwargs)
    return StructureObject.objects.create(**defaults)


def create_objectslink(**kwargs):
    defaults = {}
    defaults["code_year"] = "code_year"
    defaults["id_parent"] = "id_parent"
    defaults["id_child"] = "id_child"
    defaults["order_in_child"] = "order_in_child"
    defaults.update(**kwargs)
    return ObjectsLink.objects.create(**defaults)


def create_exam(**kwargs):
    defaults = {}
    defaults["code_year"] = "code_year"
    defaults["id_attached"] = "id_attached"
    defaults["session"] = "session"
    defaults["regime"] = "regime"
    defaults["label"] = "label"
    defaults["additionnal_info"] = "additionnal_info"
    defaults["exam_duration_m"] = "exam_duration_m"
    defaults["convocation"] = "convocation"
    defaults["is_session_2"] = "is_session_2"
    defaults["threshold_session_2"] = "threshold_session_2"
    defaults.update(**kwargs)
    return Exam.objects.create(**defaults)


class StructureObjectViewTest(unittest.TestCase):
    '''
    Tests for StructureObject
    '''
    def setUp(self):
        self.client = Client()
        self.request = RequestFactory()

    def test_list_structureobject(self):
        url = reverse('mecctable:mecctable_structureobject_list')
        r = self.request.get(url)
        a = StructureObjectListView.as_view()(r)
        self.assertEqual(a.status_code, 200)
