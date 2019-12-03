from unittest.mock import patch, Mock

from britney.errors import SporeMethodStatusError
from django.contrib.auth.models import User
from django.test import TestCase

from mecc.apps.adm.models import MeccUser
from mecc.apps.degree.models import DegreeType
from mecc.apps.institute.models import AcademicField, Institute
from mecc.apps.mecctable.models import StructureObject, ObjectsLink
from mecc.apps.training.models import Training
from mecc.apps.training.utils import reapply_respens_and_attributes_from_previous_year
from mecc.apps.years.models import UniversityYear


class RecupAtbEnsTest(TestCase):

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

    def test_training_is_not_processed_if_recup_atb_ens_flag_is_set(self):
        self.training_current_1.recup_atb_ens = True
        self.training_current_1.save()
        self.training_current_1.refresh_from_db()
        processed, message = reapply_respens_and_attributes_from_previous_year(self.training_current_1)
        self.assertFalse(processed)
        self.assertIn('Le témoin recup_atb_ens vaut True', message)

    def test_previous_year_training_has_no_ref_cpa_rof(self):
        self.training_prev_1.ref_cpa_rof = None
        self.training_prev_1.save()
        self.training_prev_1.refresh_from_db()
        processed, message = reapply_respens_and_attributes_from_previous_year(self.training_current_1)
        self.assertFalse(processed)
        self.assertIn('La formation de l\'année précédente n\'a pas de réf. ROF', message)

    def test_previous_year_training_can_not_be_found(self):
        self.training_current_1.n_train = 99999999
        self.training_current_1.save()
        self.training_current_1.refresh_from_db()
        processed, message = reapply_respens_and_attributes_from_previous_year(self.training_current_1)
        self.assertFalse(processed)
        self.assertIn('Aucune formation correspondante dans l\'année précédente', message)

    def create_structure_objects(self):
        se1_prev = StructureObject.objects.create(
            code_year=self.previous_year.code_year,
            nature='SE',
            owner_training_id=self.training_prev_1.id,
            cmp_supply_id=self.cuj.code,
            regime='E',
            session='1',
            label='Semestre 1',
            period='I',
            RESPENS_id=self.respform1.user.username,
            mutual=False,
        )
        StructureObject.objects.create(
            code_year=self.previous_year.code_year,
            nature='SE',
            owner_training_id=self.training_prev_1.id,
            cmp_supply_id=self.cuj.code,
            regime='E',
            session='1',
            label='Semestre 2',
            period='P',
            RESPENS_id=self.respform2.user.username,
            mutual=False,
        )
        se1 = StructureObject.objects.create(
            code_year=self.current_year.code_year,
            auto_id=se1_prev.id,
            nature='SE',
            owner_training_id=self.training_current_1.id,
            cmp_supply_id=self.cuj.code,
            regime='E',
            session='1',
            label='Semestre 1',
            period='I',
            RESPENS_id=None,
            external_name='First External Name',
            mutual=False,
        )
        se2 = StructureObject.objects.create(
            code_year=self.current_year.code_year,
            nature='SE',
            owner_training_id=self.training_current_1.id,
            cmp_supply_id=self.cuj.code,
            regime='E',
            session='1',
            label='Semestre 2',
            period='P',
            RESPENS_id=None,
            external_name=None,
            mutual=False,
        )
        return se1, se1_prev, se2

    def create_objectslinks(self, se1: StructureObject, se1_prev: StructureObject):
        ol_local_current = ObjectsLink.objects.create(
            code_year=self.current_year.code_year,
            id_training=self.training_current_1.id,
            id_parent=0,
            id_child=se1.id,
            order_in_child=0,
            n_train_child=self.training_current_1.id,
            nature_child='INT',
            is_imported=False,
        )
        ol_imported_current = ObjectsLink.objects.create(
            code_year=self.current_year.code_year,
            id_training=self.training_current_1.id,
            id_parent=0,
            id_child=se1.id,
            order_in_child=1,
            n_train_child=self.training_current_1.id,
            nature_child='EXT',
            is_imported=True,
        )
        ol_local_prev = ObjectsLink.objects.create(
            code_year=self.previous_year.code_year,
            id_training=self.training_prev_1.id,
            id_parent=0,
            id_child=se1_prev.id,
            order_in_child=0,
            n_train_child=self.training_prev_1.id,
            nature_child='INT',
            is_imported=False,
            coefficient=15,
            eliminatory_grade=9,
        )
        ol_imported_prev = ObjectsLink.objects.create(
            code_year=self.previous_year.code_year,
            id_training=self.training_prev_1.id,
            id_parent=0,
            id_child=se1.id,
            order_in_child=1,
            n_train_child=self.training_prev_1.id,
            nature_child='EXT',
            is_imported=True,
            coefficient=2,
            eliminatory_grade=8,
        )
        return ol_local_current, ol_imported_current, ol_local_prev, ol_imported_prev

    @patch('mecc.apps.training.utils.get_user_from_ldap')
    def test_reapply_previous_year_objectslink_attributes(self, ldap_mock):
        ldap_mock.return_value = True
        se1, se1_prev, se2 = self.setup_training_and_structure_objects()
        ol_loc_current, ol_imp_current, ol_loc_prev, ol_imp_prev = self.create_objectslinks(se1, se1_prev)

        processed, message = reapply_respens_and_attributes_from_previous_year(self.training_current_1)
        ol_loc_current.refresh_from_db()
        ol_imp_current.refresh_from_db()

        self.assertTrue(processed)
        self.assertEqual(ol_loc_current.coefficient, ol_loc_prev.coefficient)
        self.assertEqual(ol_loc_current.eliminatory_grade, ol_loc_prev.eliminatory_grade)
        self.assertEqual(ol_imp_current.coefficient, None)
        self.assertEqual(ol_imp_current.eliminatory_grade, None)

    @patch('mecc.apps.training.utils.get_user_from_ldap')
    def test_reapply_previous_year_structureobject_respens(self, ldap_mock):
        ldap_mock.return_value = True
        se1, se1_prev, se2 = self.setup_training_and_structure_objects()

        processed, message = reapply_respens_and_attributes_from_previous_year(self.training_current_1)
        se1.refresh_from_db()
        se2.refresh_from_db()

        self.assertTrue(processed)
        self.assertEqual(se1.RESPENS_id, se1_prev.RESPENS_id)
        self.assertEqual(se1.external_name, se1_prev.external_name)
        self.assertEqual(se2.RESPENS_id, None)
        self.assertEqual(se2.external_name, None)
        self.assertTrue(self.training_current_1.recup_atb_ens)

    def setup_training_and_structure_objects(self):
        self.training_current_1.ref_cpa_rof = 'ABC123'
        self.training_current_1.save()
        self.training_prev_1.ref_cpa_rof = '123ABC'
        self.training_prev_1.save()
        se1, se1_prev, se2 = self.create_structure_objects()
        return se1, se1_prev, se2

    @patch('mecc.apps.training.utils.get_user_from_ldap')
    def test_dont_reapply_respens_if_not_in_ldap(self, ldap_mock):
        response_mock = Mock()
        response_mock.status_code = 404
        ldap_mock.side_effect = SporeMethodStatusError(response_mock)

        se1, se1_prev, se2 = self.setup_training_and_structure_objects()

        processed, message = reapply_respens_and_attributes_from_previous_year(self.training_current_1)
        se1.refresh_from_db()
        se2.refresh_from_db()

        self.assertTrue(processed)
        self.assertEqual(se1.RESPENS_id, None)
        self.assertEqual(se1.external_name, se1_prev.external_name)
        self.assertEqual(se2.RESPENS_id, None)
        self.assertEqual(se2.external_name, None)
        self.assertTrue(self.training_current_1.recup_atb_ens)

    
