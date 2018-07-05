from django.db import models
from django.utils.translation import ugettext as _
from mecc.apps.degree.models import DegreeType
from mecc.apps.utils.queries import currentyear
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from mecc.apps.adm.models import Profile
from mecc.apps.mecctable.models import ObjectsLink, Exam, StructureObject
from mecc.apps.institute.models import Institute
import operator
from functools import reduce
from django.core.exceptions import ValidationError
from mecc.apps.utils.queries import update_regime_session


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

    reappli_atb = models.BooleanField(
        _("Témoin de réapplication des attributs en mode ROF"),
        default=False,
    )

    @property
    def small_dict(self):
        return dict(
            id=self.id,
            code_year=self.code_year,
            degree_type=self.degree_type.short_label,
            label=self.label,
            is_used=self.is_used,
            MECC_tab=self.MECC_tab,
            MECC_type=self.MECC_type,
            session_type=self.session_type,
            ref_cpa_rof=self.ref_cpa_rof,
            ref_si_scol=self.ref_si_scol,
            progress_rule=self.progress_rule,
            progress_table=self.progress_table,
            date_val_cmp=str(self.date_val_cmp),
            date_res_des=str(self.date_res_des),
            date_visa_des=str(self.date_visa_des),
            date_val_cfvu=str(self.date_val_cfvu),
            institutes=[{'label': e.label, 'code': e.code}
                        for e in self.institutes.all()],
            supply_cmp=self.supply_cmp,
            resp_formations=[
                e.user.username for e in self.resp_formations.all()],
            n_train=self.n_train,
            get_MECC_type_display=self.get_MECC_type_display(),
        )

    def clean_fields(self, exclude=None):
        if self.code_year is None:
            self.code_year = currentyear().code_year
        if self.n_train in ['', ' ', 0, None]:
            try:
                self.n_train = Training.objects.all().latest('id').id + 1
            except ObjectDoesNotExist:
                self.n_train = 1
        if 'CATALOGUE' in self.label.upper():
            self.progress_rule = 'A'
        if not self.MECC_tab:
            self.progress_table = 'A'

        ol = ObjectsLink.objects.filter(
            code_year=self.code_year, id_training=self.id)

        if ol and not self.MECC_tab:
            self.MECC_tab = True
            raise ValidationError({
                'MECC_tab': [_("Il y a des objets dans le tableau"), ]
            })
        if self.MECC_tab:
            self.progress_table = 'E'

        if self.has_custom_paragraph and self.degree_type != self.__original_degree_type:
            raise ValidationError({
                "degree_type": [
                    "%s %s" % (
                        _("Cette formation possède des alinéas spécifiques et/ou additionnels en"),
                        self.__original_degree_type.short_label)]
            })
        self.save()

    def __str__(self):
        return self.label

    @property
    def supply_cmp_label(self):
        """
        return label
        """
        label = self.institutes.all().get(code=self.supply_cmp).label
        return label

    @property
    def list_respform_id(self):
        """
        Return list of respform id
        """
        return [e.id for e in self.resp_formations.all()]

    @property
    def get_respform_names(self):
        """
        Return list of respform name
        """
        return ["%s %s" % (e.user.first_name.title(), e.user.last_name.title()) for e in self.resp_formations.all()]

    @property
    def list_editable_pple(self):
        """
        Return list of pple who can edit this training
        """
        can_do_alot = Profile.objects.filter(cmp=self.supply_cmp).filter(Q(code='DIRCOMP') | Q(code='RAC') | Q(code='REFAPP')
                                                                         | Q(code='GESCOL') | Q(code='DIRETU'))
        return reduce(operator.concat, [e.give_user_id for e in can_do_alot])

    @property
    def list_institutes_id(self):
        return sorted([institute.id for institute in self.institutes.all()])

    @property
    def input_opening(self):
        INPUT_CHOICE = (
            ('1', _('ouverte')),
            ('2', _('fermée en composante')),
            ('3', _('réouverte pour correction')),
            ('4', _('définitivement fermée'))
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

    @property
    def is_ECI_MECC(self):
        """
        Bool to know if this training can be see by ECI pple in their MECC pages according to :
            validées en conseil de composante, avec visa DES, sans date
            de validation en CFVU
                date_val_cmp   => True
                date_visa_des  => True
                date_val_cfvu  => False
        """
        empty = ['', ' ', None]
        if self.date_val_cmp not in empty and self.date_visa_des not in empty and self.date_val_cfvu in empty:
            return True
        else:
            return False

    @property
    def has_custom_paragraph(self):
        """
        Tell us if this training has specific or additional paragraph
        """
        specific_paragraph = SpecificParagraph.objects.filter(training=self)
        additional_paragraph = AdditionalParagraph.objects.filter(
            training=self)
        return True if specific_paragraph or additional_paragraph else False

    @property
    def has_exam(self):
        """
        Retiurn true if this training has at least one exam
        """
        struct = StructureObject.objects.filter(owner_training_id=self.id)
        exam = Exam.objects.filter(id_attached__in=[e.id for e in struct])
        return True if exam else False

    def save(self, *args, **kwargs):
        need_to_edit_struct = False
        if self.session_type != self.__original_session_type:
            self.__original_session_type = self.session_type
            need_to_edit_struct = True
        if self.MECC_type != self.__original_MECC_type:
            self.__original_MECC_type = self.MECC_type
            need_to_edit_struct = True
        if need_to_edit_struct:
            update_regime_session(self, self.MECC_type, self.session_type)

        super(Training, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(Training, self).__init__(*args, **kwargs)
        try:
            self.__original_session_type = self.session_type
            self.__original_MECC_type = self.MECC_type
            self.__original_degree_type = self.degree_type
        except DegreeType.DoesNotExist:
            pass

        if not self.code_year:
            self.code_year = currentyear().code_year
        if not self.degree_type_id:
            self.degree_type = DegreeType.objects.first()
        if not self.n_train:
            # creating n_train for ROF imported training
            self.n_train = self.id
            self.save()


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
    origin_id = models.IntegerField(
        _('ID original'), default=None, null=True, blank=True)

    def __str__(self):
        return _("Alinéa spécifique n° %s" % self.pk)


class AdditionalParagraph(models.Model):
    """
    Additional paragraph model
    """
    code_year = models.IntegerField(_('Code année'), unique=False)
    training = models.ForeignKey(Training)
    rule_gen_id = models.IntegerField(_('ID règle générale'))
    origin_id = models.IntegerField(
        _('ID original'), default=None, blank=True, null=True)

    text_additional_paragraph = models.TextField(
        _("Texte d'alinéa additionnel"))

    def __str__(self):
        return _("Alinéa additionnel n° %s" % self.pk)
