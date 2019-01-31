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
from mecc.apps.utils.queries import update_structs_regime_session, \
    delete_derogs_adds_regime
from mecc.libs.html.sanitizer import sanitize
from itertools import chain


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
    published_mecc_url = models.URLField(
        _("URL publique"),
        blank=True, null=True, default=None,
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
        Return true if this training has at least one exam
        """
        struct = StructureObject.objects.filter(owner_training_id=self.id)
        exam = Exam.objects.filter(id_attached__in=[e.id for e in struct])
        return True if exam else False

    def transform(self, mode, new_regime, new_session):
        """
        Transforms the training and related objects (SpecificParagraph,
        AdditionalParagraph, StructureObject, Exam) based on new regime
        and new session
        """
        print("IN TRANSFORM")
        # Simple flag to know if some treatment is done
        done = False
        # Code built concatenating new regime, old regime, new session, old session - Ex : CE21
        transformation_code = "{}{}{}{}".format(
            new_regime, self.MECC_type,
            new_session, self.session_type
        )
        print(transformation_code)

        def transform_exams():
            print("IN TRANSFORM_EXAMS")
            structs = StructureObject.objects.filter(owner_training_id=self.id)
            for struct in structs:
                exams = Exam.objects.filter(id_attached=struct.id)
                for exam in exams:
                    exam.regime = new_regime
                    if new_regime == 'C':
                        exam.type_ccct = 'T' if exam.convocation == 'O' else 'C'
                        exam.convocation = None
                    else:
                        exam.convocation = 'O' if exam.type_ccct == 'T' else 'N'
                        exam.type_ccct = None
                    exam.save()

        def delete_exams_session_two():
            print('IN DELETE_EXAMS_SESSION_TWO')
            structs = StructureObject.objects.filter(owner_training_id=self.id)
            for struct in structs:
                exams = Exam.objects.filter(
                    id_attached=struct.id,
                    session=2
                )
                for exam in exams:
                    exam.delete()

        def update_struct():
            """
            update regime and session of training structure according to new elements
            """
            print('UPDATE_STRUCT')
            structs = StructureObject.objects.filter(owner_training_id=self.id)
            for struc in structs:
                struc.regime = new_regime
                struc.session = new_session
                struc.save()

        def delete_derogs_adds():
            """
            Delete derogs and adds according to new regime
            """
            from mecc.apps.rules.models import Rule

            print("IN DELETE_DEROGS_ADDS")

            is_ccct = False if new_regime == 'C' else True
            is_eci = False if new_regime == 'E' else True

            rules = Rule.objects.\
                filter(
                    code_year=self.code_year,
                    is_in_use=True,
                    is_ccct=is_ccct,
                    is_eci=is_eci
                )
            rules_ids = [rule.id for rule in rules]

            derogs = SpecificParagraph.objects.\
                filter(
                    training=self,
                    rule_gen_id__in=rules_ids
                )
            derogs.delete()

            adds = AdditionalParagraph.objects.\
                filter(
                    training=self,
                    rule_gen_id__in=rules_ids
                )
            adds.delete()

        # Dict containing all codes (values) that trigger a given treatment (keys)
        treatments = {
            update_struct: ['EE12', 'EE21', 'EC11', 'EC12', 'EC21', 'EC22',
                            'CE11', 'CE12', 'CE21', 'CE22', 'CC12', 'CC21']
        }

        # Based on the mode (transform or reapply)
        # the treatment dict is enhanced
        # In reapply mode, we only want to do the update_struct() treatment
        # In transform mode we want to do al treatments
        if mode == "transform":
            transform_treatments = {
                transform_exams: ['CE11', 'CE21', 'CE12', 'CE22', 'EC11',
                                  'EC21', 'EC12', 'EC22', 'CE22', 'EC22'],
                delete_exams_session_two: ['EE12', 'CE12', 'EC12', 'CC12'],
                delete_derogs_adds: ['EC11', 'EC12', 'EC21', 'EC22',
                                     'CE11', 'CE12', 'CE21', 'CE22']
            }
            treatments.update(transform_treatments)

        # list containing all codes that trigger a treatment
        all_treatments_codes = list(chain(*treatments.values()))

        # tranformation_code (built at the beginning of the method) is evualuated
        # against all_treatments_code to determine if something has to be done
        if transformation_code in all_treatments_codes:
            # List containing the functions to launch
            to_be_done = [k for k, v in treatments.items() if transformation_code in v]
            print(to_be_done)

            # List comprehension that launch the functions stored in to_be_done
            list([x() for x in to_be_done])

            self.MECC_type = new_regime
            self.session_type = new_session
            self.save()
            done = True

        return done

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

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        self.text_specific_paragraph = sanitize(self.text_specific_paragraph)
        self.text_motiv = sanitize(self.text_motiv)


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

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        self.text_additional_paragraph = sanitize(self.text_additional_paragraph)
