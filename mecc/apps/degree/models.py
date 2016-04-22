from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

from mecc.apps.institute.models import Institute

class DegreeType(models.Model):
    """
    Degree Type model
    """
    display_order = models.IntegerField(_('Numéro ordre affichage'), unique=False)
    is_in_use = models.BooleanField(_('En service'))
    short_label = models.CharField(_('Libellé court'), max_length=40)
    long_label = models.CharField(_('Libellé long'), max_length=70)
    ROF_code = models.CharField(_('Correspondance ROF'), max_length=2, blank=True, null=True)

    def __str__(self):
        return self.short_label

    class Meta:
        ordering = ['display_order', 'short_label']
        permissions = (
            ('can_view_degree_type',
             _('Peut voir les types de diplôme')),
        )

    def get_absolute_url(self):
        return reverse('degree:type')

    def clean_fields(self, exclude=None):
        if self.display_order < 0:
            raise ValidationError({'display_order': [
                _('L\'ordre d\'affichage doit être positif.'),
                    ]})


class Degree(models.Model):
    """
    Degree model
    """
    import datetime

    label =models.TextField(_("Libellé réglementaire"))
    degree_type = models.ForeignKey(DegreeType)
    degree_type_label = models.CharField(_('Libellé du type de diplôme'), max_length=120)
    is_used = models.BooleanField(_('En service'), default=False)
    start_year = models.IntegerField(_('Code année de début de validité'))
    end_year = models.IntegerField(_('Code année de fin de validité'))
    ROF_code = models.CharField(_("Référence Programme ROF"), max_length=20)
    APOGEE_code = models.CharField(_("Référence dans le SI Scolarité (APOGEE)"), max_length=20)
    institutes = models.ManyToManyField(Institute)

    @property
    def get_id_type(self):
        return self.degree_type.id

    @property
    def get_short_label_type(self):
        return self.degree_type.short_label
