# from django.db import models
# from django.utils.translation import ugettext_lazy as _
# from mecc.apps.institute.models import Institute
#
#
# class Degree(models.Model):

#     degree_type = models.ForeignKey('DegreeType')
#     label_type = models.CharField(_('Label type'), max_length=25)
#     mention = models.CharField(_('Mention'), max_length=25)
#     speciality = models.CharField(_('Speciality'), max_length=25)
#     course = models.CharField(_('Course'), max_length=25)
#     title = models.CharField(_('Title')),
#     in_use = models.BooleanField(_('In use'))
#     start = models.IntegerField(_('Start'))
#     end = models.IntegerField(_('End'))
#     ref_formation = models.CharField(_('REF SI Formation'), max_length=25)
#     ref_scol = models.CharField(_('REF SI Scol'), max_length=25)
#     # institutes = models.ManyToManyField(Institute)
#
#     def __str__(self):
#         return '%s %s' % (self.label_type, self.mention)
#
#     class Meta:
#         ordering = ['label_type', 'mention']
#         permissions = (('can_view_degree', 'Can view degree'),)
#

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
