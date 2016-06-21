from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
import re
import datetime
from django.apps import apps


class InstituteYear(models.Model):
    """
    Institue year model
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
    pdf_doc = models.FileField(
        upload_to='doc_cadre/', blank=True, null=True
    )
    is_year_init = models.BooleanField(
        _('Initialisation des composantes effectuée'), default=False
    )

    def __str__(self):
        return self.label_year

    def save(self, *args, **kwargs):
        try:
            this = UniversityYear.objects.get(id=self.id)
            if this.pdf_doc != self.pdf_doc:
                this.pdf_doc.delete(save=False)
        except:
            pass
        super(UniversityYear, self).save(*args, **kwargs)

    def clean_fields(self, exclude=None):
        max_size = 1240000
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
        # check pdf exist on host, if it doesn't pass 0 to pdf_size
        # for other tests
        try:
            pdf_size = self.pdf_doc.size
        except (FileNotFoundError, ValueError):
            pdf_size = 0
        if self.pdf_doc:
            ext = self.pdf_doc.name.split('.')[-1]
            if ext not in ['pdf']:
                raise ValidationError(
                    {'pdf_doc': [_("Vous ne pouvez déposer que des documents \
                        pdf."), ]})
            elif pdf_size > max_size:
                raise ValidationError(
                    {'pdf_doc': [_("La taille du document ne peut être \
                        supérieure à 1MB."), ]})

    def delete(self):
        Rule = apps.get_model('rules.Rule')
        rules = Rule.objects.filter(code_year=self.code_year)
        if not len(rules) > 0:
            super(UniversityYear, self).delete()

    def get_absolute_url(self):
        return reverse('years:edit', kwargs={'code_year': self.code_year})
