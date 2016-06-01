from django.test import TestCase
from .models import Profile, MeccUser
from django.contrib.auth.models import User


class ProfileTestCase(TestCase):

    def test_profile_str(self):
        test1 = Profile.objects.create(code='TEST1', label='Test num 1')
        self.assertEqual(str(test1), test1.label)


class MeccUserTestCase(TestCase):

    def test_meccuser_str(self):
        user = User.objects.create(username='test')
        meccuser1 = MeccUser.objects.create(user=user, cmp='ECI')
        self.assertEqual(str(meccuser1), meccuser1.user.username)
