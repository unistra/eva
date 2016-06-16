from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from mecc.apps.years.models import UniversityYear
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


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
    display_order = models.IntegerField(
        _('Numéro ordre affichage'), unique=False, default=0)
    code_year = models.IntegerField(_("Code année"))
    label = models.CharField(_("Libellé"), max_length=75)
    is_in_use = models.BooleanField(_('En service'), default=True)
    is_edited = models.CharField(_('Modifiée'), max_length=4,
                                 choices=EDITED_CHOICES, default='X')
    is_eci = models.BooleanField(_('ECI'), default=False)
    is_ccct = models.BooleanField(_('CC/CT'), default=False)
    degree_type = models.ManyToManyField('degree.DegreeType')
    n_rule = models.IntegerField(_('Numéro de règle'), unique=False)

    @property
    def is_empty(self):
        """
        Return true if the rule conains any paragraph
        """
        return True if len(Paragraph.objects.filter(rule=self)) is 0 else False

    @property
    def has_parag_with_derog(self):
        """
        Return true if there is at least one derogation in paragraphs concerned
        by the rule
        """
        return True if True in [e.is_interaction for e in
                                Paragraph.objects.filter(
                                    rule=self)] else False

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
        try:
            self.n_rule = Rule.objects.all().latest('id').id + 1
        except ObjectDoesNotExist:
            self.n_rule = 1

    class Meta:
        ordering = ['display_order']
        unique_together = (("n_rule", "code_year"),)


class Paragraph(models.Model):
    """
    Paragraph model
    """
    code_year = models.IntegerField(_("Code année"), unique=False)
    rule = models.ManyToManyField(Rule)
    text_standard = models.TextField(_("Texte de l'alinéa standard"))
    is_in_use = models.BooleanField(_('En service'), default=True)
    display_order = models.IntegerField(
        _('Numéro ordre affichage'), unique=False)
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
        return reverse('rules:rule_edit', id=Rule.object.all()[0].id)

    class Meta:
        ordering = ['display_order']
