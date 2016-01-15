from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

import re


class InstituteYear(models.Model):
    id_cmp = models.IntegerField(_('ID composante'))
    code_year = models.IntegerField(_('Code année'))
    date_expected_MECC = models.DateField(
        _('Date prévisionnelle comp. MECC'), blank=True, null=True
    )
    date_last_notif = models.DateField(
        _('Date dernière notification MECC'), blank=True, null=True
    )


class UniversityYear(models.Model):
    """
    Year model
    """
    code_year = models.IntegerField(
        _('Code année'), unique=True,
        error_messages={'unique': _('Ce code année est déjà utilisé.')}
    )
    label_year = models.CharField(
        _('Libellé année'), max_length=35
    )
    is_target_year = models.BooleanField(
        _('Cible courante'), default=False
    )
    date_validation = models.DateField(
        _('Date validation cadre en CFVU'), blank=True, null=True
    )
    date_expected = models.DateField(
        _('Date prévisionnelle CFVU MECC'), blank=True, null=True
    )
    pdf_doc = models.CharField(
        _('Documents pdf'), max_length=100, blank=True
    )
    is_year_init = models.BooleanField(
        _('Initialisation des composantes effectuée'), default=False
    )

    def __str__(self):
        return 'Année universitaire %s' % label_year

    def clean_fields(self, exclude=None):
        reg = re.compile('^\d{4}$')
        if not reg.match(str(self.code_year)):
            raise ValidationError(
                {'code_year': [_('Veuillez entrer l\'année sous le format \
                AAAA.'), ]})
        if self.is_target_year:
            try:
                temp = UniversityYear.objects.get(is_target_year=True)
                if self != temp:
                    raise ValidationError({'is_target_year': [
                        _('Il y a déjà une année "cible courante".\
                        Veuillez la désactiver au préalable.'), ]})
            except UniversityYear.DoesNotExist:
                    pass

    def get_absolute_url(self):
        return reverse('years:home', args=(self.code_year,))
