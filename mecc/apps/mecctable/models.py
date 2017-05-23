from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User


class StructureObject(models.Model):
    """
    Model for teaching structure
    """
    TYPE_CHOICE = [
        ('SE', _('Semestre')),
        ('UE', _('UE')),
        ('EC', _('Élément constitutif')),
        ('ST', _('Stage')),
        ('PT', _('Projet tuteuré')),
        ('OP', _('Option')),
        ('LI', _('Liste')),
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
        _('ID automatique de l\'objet'), blank=True)
    nature = models.CharField(
        verbose_name=_('Type d\'objet'), blank=False,
        choices=TYPE_CHOICE, max_length=2)
    owner_training_id = models.IntegerField(
        _('ID de la formation propriétaire'))
    cmp_supply_id = models.CharField(
        _('ID de la composante porteuse de la formation propriétaire'),
        max_length=3)
    regime = models.CharField(
        verbose_name=_(
            'Régime de l’objet (hérité de la formation propriétaire)'),
        blank=False,
        choices=REGIME_CHOICE, max_length=1)
    session = models.CharField(
        verbose_name=_(
            'Session pour la formation (hérité de la formation propriétaire)'),
        blank=False,
        choices=SESSION_CHOICE, max_length=1)
    label = models.CharField(_("Intitulé de l'objet"), max_length=120)
    is_in_use = models.BooleanField(_('En service'), default=True)
    period = models.CharField(
        verbose_name=_("Période de l'objet"), blank=False,
        choices=PERIOD_CHOICE, max_length=1)
    ECTS_credit = models.IntegerField(_("Crédits ECTS"), blank=True, null=True)
    RESPENS_id = models.CharField(
        _("Responsable d'enseignement"), max_length=85, blank=True, null=True)
    mutual = models.BooleanField(_("Mutualisé"))

# ROF prefixed are synchronized => no input for them
    ROF_ref = models.CharField(_(
        "Référence de l'objet ROF"), max_length=20,
        null=True, blank=True)
    ROF_code_year = models.IntegerField(
        _("Année de l'objet ROF"), blank=True, null=True)
    ROF_nature = models.CharField(
        verbose_name=_("Type de l'objet ROF"), choices=TYPE_CHOICE,
        max_length=2, null=True, blank=True)
    ROF_supply_program = models.CharField(
        _("Programme porteur de l'objet ROF"),
        max_length=20, null=True, blank=True)

    ref_si_scol = models.CharField(
        _("Référence SI Scolarité"), max_length=20, null=True, blank=True)

    external_name = models.CharField(
        _("Intervenant exterieur"), max_length=240, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if self.auto_id in ['', ' ', 0, None]:
            try:
                self.auto_id = StructureObject.objects.all(
                    ).latest('id').id + 1
            except ObjectDoesNotExist:
                self.auto_id = 1
        super(StructureObject, self).save(*args, **kwargs)

    @property
    def get_children(self):
        """
        Return list of direct children
        """
        return [StructureObject.objects.get(
            id=e.id_child) for e in ObjectsLink.objects.filter(
                id_parent=self.id)]

    @property
    def get_respens_name(self):
        """
        Return last_name and first_name of respens
        """
        if self.RESPENS_id:
            user = User.objects.get(username=self.RESPENS_id)
            return user.last_name + " " + user.first_name
        else:
            return ""


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
    n_train_child = models.IntegerField(
        _("ID interne de la formation d’origine du fils"))
    nature_child = models.CharField(
        verbose_name=_("Nature du fils"), blank=False,
        choices=NATURE_CHOICE, max_length=3)
    coefficient = models.DecimalField(
        max_digits=4, decimal_places=2,
        verbose_name=_("Coefficient de l’objet (au sein de ce père)"),
        null=True, blank=True)
    eliminatory_grade = models.IntegerField(
        _("Note seuil sur cet objet (au sein de ce père)"),
        default=None, null=True, blank=True)
    is_imported = models.NullBooleanField(
        _('Est importé'), null=True, blank=True)


    @property
    def nature_parent(self):
        parent = StructureObject.objects.get(
            id=self.id_parent) if self.id_parent not in [0, '0'] else None

        if parent:
            return parent.nature
        else:
            return None

    @property
    def depth(self, count=0):
        def get_depth(link, count=0):
            if link.id_parent in [0, '0']:
                return count
            else:
                gparent = ObjectsLink.objects.get(id_child=link.id_parent)
                return get_depth(gparent, count+1)
        return range(get_depth(self))


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
        _("Note seuil de l'épreuve"), null=True)
    is_session_2 = models.BooleanField(_("Témoin Report session 2"))
    threshold_session_2 = models.IntegerField(_("Seuil de report session 2"))
