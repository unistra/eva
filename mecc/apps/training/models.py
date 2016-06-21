from django.db import models
from django.utils.translation import ugettext as _
from mecc.apps.degree.models import DegreeType


class Training(models.Model):
    """
    Training model
    """

    MECC_TYPE_CHOICE = (('E', _('ECI')), ('C', _('CC/CT')))
    SESSION_TYPE_CHOICE = (('1', _('session unique')), ('2', _('2 sessions')))
    PROGRESS_CHOICE = (('E', _('En cours')), ('A', _('Achevée')))

    code_year = models.IntegerField(_("Code année"), unique=False)
    degree_type = models.ForeignKey(
        DegreeType, related_name='degree_type', verbose_name='Type de diplôme')
    label = models.TextField(_('Intitulé de formation'))
    is_used = models.BooleanField(_('En service'), default=True)
    MECC_tab = models.BooleanField(_('Témoin Tableau MECC'), default=True)
    MECC_type = models.CharField(
        _('Régime MECC de la formation'), blank=False,
        choices=MECC_TYPE_CHOICE, max_length=1
    )
    session_type = models.CharField(
        _('Session pour la formation'), blank=False,
        choices=SESSION_TYPE_CHOICE, max_length=1
    )
    ref_cpa_rof = models.CharField(_('Référence CP Année ROF'), max_length=20)
    ref_si_scol = models.CharField(_('Référence SI Scol'), max_length=20)
    progress_rule = models.CharField(
        _('Avancement de la saisie des règles'), choices=PROGRESS_CHOICE,
        max_length=1
    )
    progress_table = models.CharField(
        _('Avancement de la saisie du tableau MECC'), choices=PROGRESS_CHOICE,
        max_length=1
    )
    MECC_TYPE_CHOICE = (('E', _('ECI')), ('C', _('CC/CT')),)
    date_val_cmp = models.DateField(
        _('Date de validation en conseil de composante'), blank=True, null=True
    )
    date_res_des = models.DateField(
        _('Date de réserve DES'), blank=True, null=True
    )
    date_visa_des = models.DateField(
        _('Date de visa DES'), blank=True, null=True
    )
    date_val_cfvu = models.DateField(
        _('Date de validation en CFVU'), blank=True, null=False
    )

    @property
    def input_opening(self):
        INPUT_CHOICE = (
            ('1', _('Ouverte')),
            ('2', _('Fermée en composante')),
            ('3', _('Rouverte pour correction')),
            ('4', _('Définitivement fermée'))
        )
        empty = ['', ' ', None]
        if self.date_val_cfvu not in empty:
            return INPUT_CHOICE[3]
        if self.date_val_cmp in empty:
            return INPUT_CHOICE[0]
        if self.date_val_cmp not in empty and self.date_res_des in empty:
            return INPUT_CHOICE[1]
        if self.date_val_cmp not in empty and self.date_res_des not in empty:
            return INPUT_CHOICE[2]
        return None


class TrainingCMP(models.Model):
    """
    Intermediary model allowing connection with year, training and cmp
    (institute)
    """
    code_year = models.IntegerField(_("Code année"), unique=False)
    id_training = models.ForeignKey('training.Training')
    degree_type = models.ForeignKey('degree.DegreeType')
    supply_cmp = models.BooleanField(_('Composante porteuse'))

    def clean_fields(self):
        same = TrainingCMP.objects.filter(
            code_year=self.code_year,
            id_training=self.id_training,
            degree_type=self.degree_type
        )
        if same:
            self.supply_cmp = False
        else:
            self.supply_cmp = True


class TrainingResp(models.Model):
    """
    Model for training responsable with training CMP, user, and
    """
    training_cmp = models.ForeignKey('training.TrainingCMP')
    resp_formation = models.ForeignKey('adm.MeccUser')
