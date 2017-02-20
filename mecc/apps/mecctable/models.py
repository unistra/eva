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
    label = models.CharField(_("Intitulé de l'objet"), max_length=120)
    is_in_use = models.BooleanField(_('En service'), default=True)
    period = models.CharField(
        verbose_name=_("Période de l'objet"), blank=False,
        choices=PERIOD_CHOICE, max_length=1)
    ECTS_credit = models.IntegerField(_("Crédits ECTS"))
    RESPENS_id = models.CharField(
        _("Responsable d'enseignement"), max_length=85)
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


class ObjectsLink(models.Model):
    NATURE_CHOICE = [
        ("INT", _("ID formation d’origine = ID formation contexte")),
        ("EXT", _("ID formation d’origine ≠ ID formation contexte")),
    ]
    code_year = models.IntegerField(_("Code année"), unique=False)
    id_training = models.IntegerField(
        _("ID interne de la formation"))  # context
    id_parent = models.IntegerField(_("ID objet père"))
    id_child = models.IntegerField(_("ID objet fils"))
    order_in_child = models.IntegerField(
        _("Numéro d'ordre fils (au sein du père)"))
    id_original_training_child = models.IntegerField(
        _("ID interne de la formation d’origine du fils"))
    nature_child = models.CharField(
        verbose_name=_("Nature du fils"), blank=False,
        choices=NATURE_CHOICE, max_length=3)
    coefficient = models.DecimalField(
        verbose_name=_("Coefficient de l’objet (au sein de ce père)"),
        max_digits=2, decimal_places=1)
    eliminatory_grade = models.IntegerField(
        _("Note éliminatoire sur cet objet (au sein de ce père)"),
        default=None)


class Exam(models.Model):
    REGIME_CHOICE = [
        ('E', _('ECI')),
        ('C', _('CC/CT')),
    ]

    SESSION_CHOICE = [
        ('1', _('Session unique')),
        ('2', _('2 sessions')),
    ]
    TYPE_EXAM_CHOICES = [
        ('E', _("Écrit")),
        ('O', _("Oral")),
        ('A', _("Autre")),
    ]
    CONVOCATION_CHOICE = [
        ('O', _("Oui")),
        ('N', _("None")),
        ('X', None)  # Non applicable au régime CC/CT

    ]
    TYPECCCT_CHOICE = [
        ('C', _("CC")),
        ('T', _("CT")),
        ('X', None)  # Non applicable au régime ECI
    ]

    code_year = models.IntegerField(_("Code année"), unique=False)
    id_attached = models.IntegerField(_("ID objet de rattachement (contexte)"))
    session = models.CharField(
        verbose_name=_("Session de l'épreuve"), blank=False,
        choices=SESSION_CHOICE, max_length=1)
    _id = models.IntegerField(_("ID interne de l'épreuve"))
    regime = models.CharField(
        verbose_name=_("Régime de l'épreuve"), blank=False,
        choices=REGIME_CHOICE, max_length=1)
    type_exam = models.CharField(
        verbose_name=_(""), choices=TYPE_EXAM_CHOICES, max_length=1)
    label = models.CharField(_("Intitulé de l'épreuve"), max_length=25)
    additionnal_info = models.CharField(
        _("Complément d’information sur l’épreuve"),
        max_length=200)
    exam_duration_h = models.IntegerField(_("Durée de l’épreuve-Heures"))
    exam_duration_m = models.IntegerField(_("Durée de l’épreuve-Minutes"))
    convocation = models.CharField(
        verbose_name=_("Convocation"), choices=CONVOCATION_CHOICE,
        max_length=1)
    type_ccct = models.CharField(
        verbose_name=_("Type CC ou CT"), choices=TYPECCCT_CHOICE, max_length=1
    )
    coefficient = models.DecimalField(
        verbose_name=_("Coefficient de l'épreuve"),
        max_digits=2, decimal_places=1)
    eliminatory_grade = models.IntegerField(
        _("Note éliminatoire de l'épreuve"))
    is_session_2 = models.BooleanField(_("Témoin Report session 2"))
    threshold_session_2 = models.IntegerField(_("Seuil de report session 2"))
