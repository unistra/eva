from django.db import models
from django.utils.translation import ugettext as _
from mecc.apps.degree.models import DegreeType
from mecc.apps.utils.querries import currentyear
from django.core.exceptions import ObjectDoesNotExist


class Training(models.Model):
    """
    Training model
    """

    MECC_TYPE_CHOICE = (
        ('E', _('ECI')),
        ('C', _('CC/CT')),
        ('N', _('Non applicable'))
    )
    SESSION_TYPE_CHOICE = (
        ('1', _('Session unique')),
        ('2', _('2 sessions')),
        ('0', _('Non applicable'))
    )
    PROGRESS_CHOICE = (('E', _('En cours')), ('A', _('Achevée')))

    code_year = models.IntegerField(_("Code année"), unique=False)
    degree_type = models.ForeignKey(
        DegreeType, related_name='degree_type', verbose_name='Type de diplôme')
    label = models.TextField(_('Intitulé de formation'))
    is_used = models.BooleanField(_('En service'), default=True)
    MECC_tab = models.BooleanField(_('Témoin Tableau MECC'), default=True)
    MECC_type = models.CharField(
        verbose_name=_('Régime MECC de la formation'), blank=False,
        choices=MECC_TYPE_CHOICE, max_length=1)
    session_type = models.CharField(
        _('Session pour la formation'), blank=False,
        choices=SESSION_TYPE_CHOICE, max_length=1)
    ref_cpa_rof = models.CharField(
        _('Référence CP Année ROF'), max_length=20, null=True, blank=True)
    ref_si_scol = models.CharField(
        _('Référence SI Scol'), max_length=20, null=True, blank=True)
    progress_rule = models.CharField(
        _('Avancement de la saisie des règles'), choices=PROGRESS_CHOICE,
        max_length=1, default="E")
    progress_table = models.CharField(
        _('Avancement de la saisie du tableau MECC'), choices=PROGRESS_CHOICE,
        max_length=1, default="E")
    date_val_cmp = models.DateField(
        _('Date de validation en conseil de composante'),
        blank=True, null=True)
    date_res_des = models.DateField(
        _('Date de réserve DES'), blank=True, null=True)
    date_visa_des = models.DateField(
        _('Date de visa DES'), blank=True, null=True)
    date_val_cfvu = models.DateField(
        _('Date de validation en CFVU'), blank=True, null=True)

    institutes = models.ManyToManyField('institute.Institute')
    supply_cmp = models.CharField(_('porteuse'), max_length=3, blank=True)
    resp_formations = models.ManyToManyField('adm.MeccUser')
    n_train = models.IntegerField(
        _('Numéro de règle'), unique=False, null=True)

    def clean_fields(self, exclude=None):
        if self.code_year is None:
            self.code_year = currentyear().code_year
        if self.n_train in ['', ' ', 0, None]:
            try:
                self.n_train = Training.objects.all().latest('id').id + 1
            except ObjectDoesNotExist:
                self.n_train = 1

    def __str__(self):
        return self.label

    @property
    def input_opening(self):
        INPUT_CHOICE = (
            ('1', _('ouverte')),
            ('2', _('fermée en composante')),
            ('3', _('rouverte pour correction')),
            ('4', _('définitivement fermée'))
        )
        empty = ['', ' ', None]
        if self.date_val_cfvu not in empty:
            return INPUT_CHOICE[3][1]
        if self.date_val_cmp in empty:
            return INPUT_CHOICE[0][1]
        if self.date_val_cmp not in empty and self.date_res_des in empty:
            return INPUT_CHOICE[1][1]
        if self.date_val_cmp not in empty and self.date_res_des not in empty:
            return INPUT_CHOICE[2][1]
        return None


class SpecificParagraph(models.Model):
    """
    Specific paragraph model
    """
    TYPE_PARAPGRAPH = (('D', _('Dérogatoire')), ('C', _('Composante')))
    code_year = models.IntegerField(_("Code année"), unique=False)
    training = models.ForeignKey(Training)
    rule_gen_id = models.IntegerField(_('ID règle générale'))
    paragraph_gen_id = models.IntegerField(_('ID alinéa général'))
    type_paragraph = models.CharField(
        _('Type alinéa'), choices=TYPE_PARAPGRAPH, max_length=1)
    text_specific_paragraph = models.TextField(_("Texte d'alinéa spécifique"))
    text_motiv = models.TextField(_("Texte de motivation"))

    def __str__(self):
        return _("Alinéa spécifique n° %s" % self.pk)


class AdditionalParagraph(models.Model):
    code_year = models.IntegerField(_('Code année'), unique=False)
    training = models.ForeignKey(Training)
    rule_gen_id = models.IntegerField(_('ID règle générale'))
    text_additional_paragraph = models.TextField(
        _("Texte d'alinéa additionnel"))

    def __str__(self):
        return _("Alinéa additionnel n° %s" % self.pk)
