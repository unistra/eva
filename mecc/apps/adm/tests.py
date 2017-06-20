from django.test import TestCase
from .models import Profile, MeccUser
from django.contrib.auth.models import User


class ProfileTestCase(TestCase):

    def test_profile_str(self):
        test1 = Profile.objects.create(code='TEST1', label='Test num 1')
        self.assertEqual(str(test1), test1.label)

    def test_give_user_id_property(self):
        p1 = Profile.objects.create(
            code='ECI', label="Membre de la commission ECI")
        Profile.objects.create(code='DIRCOMP', label="Directeur de composante")
        User.objects.create_user(username="TEST1")
        user = User.objects.create(username='test')
        meccuser = MeccUser.objects.get(user=user)
        meccuser.profile.add(p1)
        self.assertEqual(p1.give_user_id, [meccuser.id])


class MeccUserTestCase(TestCase):

    def test_meccuser_str(self):
        user = User.objects.create(username='test')
        meccuser1 = MeccUser.objects.get(user=user)
        self.assertEqual(str(meccuser1), meccuser1.user.username)
