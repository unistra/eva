"""
Model for years with institute year and university year
"""
import datetime
import re
from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _
from mecc.apps.files.models import FileUpload


class InstituteYear(models.Model):
    """
    Institute year model
    """
    id_cmp = models.IntegerField(_('ID composante'))
    code_year = models.IntegerField(_('Code année'))
    date_expected_MECC = models.DateField(
        _('Date prévisionnelle comp. MECC'), blank=True, null=True
    )
    date_last_notif = models.DateField(
        _('Date dernière notification MECC'), blank=True, null=True
    )

    def is_expected_date_late(self):
        if isinstance(self.date_expected_MECC, datetime.date):
            current = UniversityYear.objects.get(is_target_year=True)
            if isinstance(current.date_expected, datetime.date):
                return True if (current.date_expected <=
                                self.date_expected_MECC) else False
        return None


class UniversityYear(models.Model):
    """
    Year model
    """
    code_year = models.IntegerField(
        _('Code année'), unique=True,
        error_messages={'unique': _('Ce code année est déjà utilisé.')}
    )
    label_year = models.CharField(
        _('Libellé année'), max_length=35, blank=True,
    )
    is_target_year = models.BooleanField(
        _('Cible courante')
    )
    date_validation = models.DateField(
        _('Date validation cadre en CFVU'), blank=True, null=True
    )
    date_expected = models.DateField(
        _('Date prévisionnelle CFVU MECC'), blank=True, null=True
    )
    is_year_init = models.BooleanField(
        _('Initialisation des composantes effectuée'), default=False
    )

    def __str__(self):
        return self.label_year

    def save(self, *args, **kwargs):
        try:
            this = UniversityYear.objects.get(id=self.id)
        except:
            pass
        super(UniversityYear, self).save(*args, **kwargs)

    def clean_fields(self, exclude=None):
        if self.code_year in set(
                [e.code_year for e in InstituteYear.objects.all()]):
            self.is_year_init = True
        else:
            self.is_year_init = False
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

    def getPdf(self):
        return FileUpload.objects.filter(
            object_id=self.id).first()

    def delete(self):
        Rule = apps.get_model('rules.Rule')
        rules = Rule.objects.filter(code_year=self.code_year)
        pdf = self.getPdf()
        if not len(rules) > 0:
            if pdf:
                pdf.file.delete()
                pdf.delete()
            super(UniversityYear, self).delete()

    def get_absolute_url(self):
        return reverse('years:edit', kwargs={'code_year': self.code_year})
