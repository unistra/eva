from django.db import models
from django.utils.translation import ugettext as _
from mecc.apps.degree.models import DegreeType
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from mecc.apps.years.models import UniversityYear
from django.db.models import Q


class Impact(models.Model):
    """
    Impact model
    """
    code = models.IntegerField(_("Code impact"), unique=True)
    description = models.CharField(_("Description impact "), max_length=250)

    def __str__(self):
        return "%s - %s" % (self.code, self.description)


class Rule(models.Model):
    """
    Rule model
    """
    EDITED_CHOICES = (
        ('O', _('Oui')),
        ('N', _('Non')),
        ('X', _('Nouvelle')),
    )

    display_order = models.IntegerField(_('Numéro ordre affichage'), unique=False, default=0)
    code_year = models.IntegerField(_("Code année"))
    label = models.CharField(_("Libellé"), max_length=75)
    is_in_use = models.BooleanField(_('En service'), default=True)
    is_edited = models.CharField(_('Modifiée'), max_length=4,
                                 choices=EDITED_CHOICES, default='X')
    is_eci = models.BooleanField(_('ECI'), default=False)
    is_ccct = models.BooleanField(_('CC/CT'), default=False)
    degree_type = models.ManyToManyField(DegreeType)

    @property
    def is_empyt(self):
        """
        Return true if the rule conains any paragraph
        """
        return True if len(Paragraph.objects.filter(rule=self)) is 0 else False


    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse('rules:list')

    def clean_fields(self, exclude=None):
        self.code_year = list(UniversityYear.objects.filter(
            Q(is_target_year=True))).pop(0).code_year
        if self.display_order < 0:
            raise ValidationError({'display_order': [
                _('L\'ordre d\'affichage doit être positif.'),
            ]})

    class Meta:
        ordering = ['display_order']


class Paragraph(models.Model):
    """
    Paragraph model
    """
    code_year = models.IntegerField(_("Code année"), unique=False)
    rule = models.ManyToManyField(Rule)
    text_standard = models.TextField(_("Texte de l'alinéa standard"))
    is_in_use = models.BooleanField(_('En service'), default=True)
    display_order = models.IntegerField(_('Numéro ordre affichage'), unique=False)
    is_cmp = models.BooleanField(_('Alinéa de composante'))
    is_interaction = models.BooleanField(_('Interaction'))
    text_derog = models.TextField(_("Texte de consigne pour la saisie de \
        l'alinéa dérogatoire (ou de composante)"), blank=True)
    text_motiv = models.TextField(_("Texte de consigne pour la saisie des \
        motivations"), blank=True)
    impact = models.ManyToManyField(Impact)

    def __str__(self):
        return "Alinéa n° %s" % self.pk

    def get_absolute_url(self):
        return reverse('rules:rule_edit', id=rule.object.all()[0].id)

    class Meta:
        ordering = ['display_order']
