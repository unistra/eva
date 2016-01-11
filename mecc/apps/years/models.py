from django.db import models
from django.utils.translation import ugettext_lazy as _


class UniversityYear(models.Model):
    """
    Year model
    """
    code_year = models.IntegerField(_('Code Année'), unique=True)
    label_year = models.CharField(_('Libellée Année'), max_length=9)
    is_target_year = models.BooleanField(_('Cible Courante'), default=False)
    date_validation = models.DateField(_('Date validation du cadre en CFVU'))
    date_expected = models.DateField(_('Date prévisionnelle de la CFVU MECC'))
    pdf_doc = models.CharField(_('Documents cadre (pdf)'), max_length=100, blank=True)
    is_year_init = models.BooleanField(_('Initialisation Composante'), default=False)
