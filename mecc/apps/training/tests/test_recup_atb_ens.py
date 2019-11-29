from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test import TestCase

from mecc.apps.adm.models import MeccUser
from mecc.apps.degree.models import DegreeType
from mecc.apps.institute.models import AcademicField, Institute
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
