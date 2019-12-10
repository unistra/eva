from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from mecc.apps.adm.models import MeccUser
from mecc.apps.degree.models import DegreeType
from mecc.apps.institute.models import Institute, AcademicField
from mecc.apps.training.models import Training
from mecc.apps.training.utils import reapply_attributes_previous_year
from mecc.apps.years.models import UniversityYear


class ReappliAtbTest(TestCase):

    def setUp(self) -> None:
        licence = DegreeType.objects.create(
            display_order=1, is_in_use=True, short_label='Licence', long_label='Licence',
        )
        field = AcademicField.objects.create(name='Field')
        user1 = User.objects.create_user(username='user1', password='password')
        user2 = User.objects.create_user(username='user2', password='password')
        self.cuj = Institute.objects.create(code='CUJ', label='CUJ', field=field)
        self.current_year = UniversityYear.objects.create(
            code_year=2019, label_year='Année 2019/2020', is_target_year=True,
        )
        self.previous_year = UniversityYear.objects.create(
            code_year=2018, label_year='Année 2018/2019', is_target_year=False,
        )
        self.training_prev_1 = Training.objects.create(
            code_year=self.previous_year.code_year,
            degree_type=licence,
            label='Formation un N-1',
            MECC_type='E',
            session_type='1',
            supply_cmp=self.cuj.code,
            MECC_tab=False,
        )
        self.training_prev_1.institutes.add(self.cuj)
        self.respform1 = MeccUser.objects.get(pk=user1.id)
        self.respform2 = MeccUser.objects.get(pk=user2.id)
        self.training_prev_1.resp_formations.add(self.respform1, self.respform2)
        self.training_prev_2 = Training.objects.create(
            code_year=self.previous_year.code_year,
            degree_type=licence,
            label='Formation deux N-1',
            MECC_type='E', session_type='1',
            supply_cmp=self.cuj.code,
            MECC_tab=True,
        )
        self.training_prev_2.institutes.add(self.cuj)
        self.training_prev_2.resp_formations.add(self.respform1)
        self.training_current_1 = Training.objects.create(
            code_year=self.current_year.code_year,
            degree_type=licence,
            label='Formation un N',
            MECC_type='E',
            session_type='1',
            supply_cmp=self.cuj.code,
            n_train=self.training_prev_1.id,
        )
        self.training_current_2 = Training.objects.create(
            code_year=self.current_year.code_year,
            degree_type=licence,
            label='Formation deux N',
            MECC_type='E',
            session_type='1',
            supply_cmp=self.cuj.code,
            n_train=self.training_prev_2.id,
        )

    @patch('mecc.apps.utils.ws.get_user_from_ldap')
    def test_training_without_n_train_is_not_processed(self, mock):
        mock.return_value = True
        self.training_current_1.n_train = None
        self.training_current_1.reappli_atb = False
        self.training_current_1.save()
        self.training_current_2.n_train = None
        self.training_current_2.reappli_atb = False
        self.training_current_2.save()
        processed, skipped = reapply_attributes_previous_year(self.cuj, self.current_year)
        self.assertEqual(len(processed), 0)
        self.assertEqual(len(skipped), 2)

    @patch('mecc.apps.training.utils.get_user_from_ldap')
    def test_training_with_reappli_atb_set_is_not_processed(self, mock):
        mock.return_value = True
        self.training_current_1.reappli_atb = True
        self.training_current_1.save()
        processed, skipped = reapply_attributes_previous_year(self.cuj, self.current_year)
        self.assertEqual(len(processed), 1)
        self.assertEqual(len(skipped), 1)
        self.assertIn(self.training_current_1, skipped)
        self.assertIn(self.training_current_2, processed)

    @patch('mecc.apps.training.utils.get_user_from_ldap')
    def test_training_is_updated_with_previous_values(self, mock):
        mock.return_value = True
        self.training_current_1.MECC_tab = True
        self.training_current_2.MECC_tab = False
        processed, skipped = reapply_attributes_previous_year(self.cuj, self.current_year)
        self.assertEqual(len(processed), 2)
        self.training_current_1.refresh_from_db()
        self.assertEqual(self.training_current_1.MECC_tab, False)
        self.training_current_2.refresh_from_db()
        self.assertEqual(self.training_current_2.MECC_tab, True)
        self.assertEqual(len(self.training_current_1.resp_formations.all()), 2)
        self.assertIn(self.respform1, self.training_current_1.resp_formations.all())
        self.assertIn(self.respform2, self.training_current_1.resp_formations.all())
        self.assertEqual(len(self.training_current_2.resp_formations.all()), 1)
        self.assertIn(self.respform1, self.training_current_2.resp_formations.all())

    @patch('mecc.apps.training.utils.get_user_from_ldap')
    def test_n_train_referencing_non_existing_training_is_not_processed(self, mock):
        mock.return_value = True
        self.training_current_1.n_train = 999999
        self.training_current_1.save()
        with self.assertLogs(logger='mecc.apps.training.utils', level='ERROR') as cm:
            processed, skipped = reapply_attributes_previous_year(self.cuj, self.current_year)
            self.assertEqual(len(skipped), 1)
            self.assertIn(self.training_current_1, skipped)
            message = "{}Training #{} has n_train attribute {} but training #{} does not exist".format(
                'ERROR:mecc.apps.training.utils:',
                self.training_current_1.id,
                self.training_current_1.n_train, self.training_current_1.n_train)
            self.assertIn(message, cm.output)

    @patch('mecc.apps.training.utils.get_user_from_ldap')
    def test_even_if_there_is_no_corresponding_training_in_previous_year_flag_is_set_to_true(self, ldap_mock):
        ldap_mock.return_value = True
        self.training_prev_2.delete()
        self.training_current_2.n_train = self.training_current_2.id
        self.training_current_2.save()

        processed, skipped = reapply_attributes_previous_year(self.cuj, self.current_year)
        self.training_current_1.refresh_from_db()
        self.training_current_2.refresh_from_db()

        self.assertEqual(len(processed), 1)
        self.assertEqual(len(skipped), 1)
        self.assertListEqual(skipped, [self.training_current_2])
        self.assertTrue(self.training_current_1.reappli_atb)
        self.assertTrue(self.training_current_2.reappli_atb)
