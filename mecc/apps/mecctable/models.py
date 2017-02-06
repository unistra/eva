from django.db import models
from django.utils.translation import ugettext as _


class StructureObject(models.Model):
    """
    Model for teaching structure
    """
    TYPE_CHOICE = [
        ('SE', _('Semestre')),
        ('OP', _('Option')),
        ('LI', _('Liste')),
        ('UE', _('UE')),
        ('EC', _('Élément constitutif')),
        ('ST', _('Stage')),
        ('PT', _('Projet tutoré')),
    ]
    REGIME_CHOICE = [
        ('E', _('ECI')),
        ('C', _('CC/CT')),
    ]

    SESSION_CHOICE = [
        ('1', _('Session unique')),
        ('2', _('2 sessions')),
    ]

    PERIOD_CHOICE = [
        ('I', _("Semestre impair")),
        ('P', _("Semestre pair")),
        ('A', _("Année")),
    ]

    code_year = models.IntegerField(
        _("Code année"), unique=False)
    auto_id = models.IntegerField(
        _('ID automatique de l\'objet'), unique=True)
    nature = models.CharField(
        verbose_name=_('Type d\'objet'), blank=False,
        choices=TYPE_CHOICE, max_length=2)
    owner_training_id = models.IntegerField(
        _('ID de la formation propriétaire'))
    cmp_supply_id = models.IntegerField(
        _('ID de la composante porteuse de la formation propriétaire'))
    regime = models.CharField(
        verbose_name=_(
            'Régime de l’objet (hérité de la formation propriétaire)'),
        blank=False,
        choices=REGIME_CHOICE, max_length=1)
    session = models.CharField(
        verbose_name=_(
            'Sessions pour la formation (hérité de la formation propriétaire)'),
        blank=False,
        choices=SESSION_CHOICE, max_length=1)
    label = models.CharField(_('Intitulé de l\'objet'), max_length=120)
    is_in_use = models.BooleanField(_('En service'), default=True)
    period = models.CharField(
        verbose_name=_("Période de l'objet"), blank=False,
        choices=PERIOD_CHOICE, max_length=1)
    ECTS_credit = models.IntegerField(_("Crédits ECTS"))
    RESPENS_id = models.CharField(_("ID du responsable d'enseignement"))
    mutual = models.BooleanField(_("Mutualisé"))

# ROF prefixed are synchronized => no input for them
    ROF_ref = models.CharField(_("Référence de l'objet ROF"), max_length=20)
    ROF_code_year = models.IntegerField(_("Année de l'objet ROF"))
    ROF_nature = models.CharField(
        verbose_name=_("Type de l'objet ROF"), choices=TYPE_CHOICE,
        max_length=2)
    ROF_supply_program = models.CharField(
        _("Programme porteur de l'objet ROF"), max_length=20)

    ref_si_scol = models.CharField(_("Référence SI Scolarité"), max_length=20)
