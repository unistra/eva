from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


class DegreeType(models.Model):
    display_order = models.IntegerField(_('Numéro ordre affichage'), unique=True)
    is_in_use = models.BooleanField(_('En service'))
    short_label = models.CharField(_('Libellé court'), max_length=40)
    long_label = models.CharField(_('Libellé long'), max_length=70)
    mecc_cat = models.CharField(_('Catégorie MECC'), max_length=25, blank=True, null=True)

    def __str__(self):
        return self.short_label

    class Meta:
        ordering = ['display_order']

    def get_absolute_url(self):
        return reverse('degree:type')


class Degree(models.Model):
    import datetime

    YEAR_CHOICES = [(y,y) for y in range(1900, datetime.date.today().year+5)]
    degree_type = models.ForeignKey(DegreeType)
    label_type = models.CharField(_('Libellé type'), max_length=35)
    spe = models.CharField(_('Spécialité'), max_length=35)
    parcours = models.CharField(_('Parcours'), max_length=35)
    label = models.CharField(_('Intitulé'), max_length=35)
    is_in_use = models.BooleanField(_('En service'), default=False)
    start = models.IntegerField(_('Début'), choices=YEAR_CHOICES)
    end = models.IntegerField(_('Fin'), choices=YEAR_CHOICES)
