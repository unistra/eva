from django.db import models
from django.utils.translation import ugettext as _
from mecc.apps.degree.models import DegreeType
from django.core.urlresolvers import reverse

class Impact(models.Model):
    code = models.IntegerField(_("Code impact"), unique=True)
    description = models.CharField(_("Description impact "), max_length=250)

    def __str__(self):
        return "%s - %s" % (self.code, self.description)


class Rule(models.Model):

    EDITED_CHOICES = (
        ('O', _('Oui')),
        ('N', _('Non')),
        ('X', _('Nouvelle')),
    )

    display_order = models.IntegerField(_('Numéro ordre affichage'), unique=False)
    code_year = models.IntegerField(_("Code année"))
    label = models.CharField(_("Libellé"), max_length=75)
    is_in_use = models.BooleanField(_('En service'))
    is_edited = models.CharField(_('Modifiée'), max_length=4,
        choices=EDITED_CHOICES, default='X')
    is_eci = models.BooleanField(_('ECI'), default=False)
    is_ccct = models.BooleanField(_('CC/CT'), default=False)
    degree_type = models.ManyToManyField(DegreeType)

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse('rules:list')

    class Meta:
        ordering = ['display_order']

class Paragraph(models.Model):
    code_year = models.IntegerField(_("Code année"))
    rule = models.ManyToManyField(Rule)
    text_standard = models.TextField(_("Texte de l'alinéa standard"))
    is_in_use = models.BooleanField(_('En service'))
    display_order = models.IntegerField(_('Numéro ordre affichage'), unique=False)
    is_cmp = models.BooleanField(_('Alinéa de composante'))
    is_interaction = models.BooleanField(_('Interaction'))
    text_derog = models.TextField(_("Texte de consigne pour la saisie de \
        l'alinée dérogatoire (ou de composante)"))
    text_motiv = models.TextField(_("Texte de consigne pour la saisie des \
        motivations"))
    impact = models.ManyToManyField(Impact)

    def __str__(self):
        return "Alinéa n° %s" % self.pk
