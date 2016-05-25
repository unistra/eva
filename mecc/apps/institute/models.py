from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from mecc.apps.adm.models import MeccUser


class AcademicField(models.Model):
    """
    Academic field model
    """
    name = models.CharField(_('Domaine'), max_length=70)

    def __str__(self):
        return self.name


class Institute(models.Model):
    """
    Institute model
    """
    field_choice = AcademicField.objects.all()

    code = models.CharField(_('Code composante'), max_length=3)
    is_on_duty = models.BooleanField(_('En service'))
    label = models.CharField(_('Libellé composante'), max_length=85)
    field = models.ForeignKey(AcademicField, blank=False)
    id_dircomp = models.CharField(
        _('Directeur de composante'), max_length=65, blank=True)
    id_rac = models.CharField(
        _('Responsable administratif'), max_length=65, blank=True)
    dircomp = models.ForeignKey(
        MeccUser, related_name='dircomp', blank=True, null=True)
    rac = models.ForeignKey(
        MeccUser, related_name='racs', blank=True, null=True)
    diretu = models.ManyToManyField(
        MeccUser, related_name='diretu', blank=True)
    scol_manager = models.ManyToManyField(
        MeccUser, related_name='scol_managers', blank=True)
    ROF_code = models.CharField(
        _('Code RNE'), max_length=10, blank=True, null=True)
    ROF_support = models.BooleanField(_('Appui ROF'), default=False)

    def clean_fields(self, exclude=None):
        try:
            temp = Institute.objects.get(code=self.code)
            if self != temp:
                raise ValidationError({'code': [
                    _('Le code composante "%s" est déjà utilisé.' % self.code),
                        ]})
        except Institute.DoesNotExist:
                pass

    def get_absolute_url(self):
        return reverse('institute:home', args=(self.code,))

    def __str__(self):
        return "%s - %s" % (self.code, self.label)

    class Meta:
        permissions = (
            ('can_view_institute',
             _('Peut voir les composantes')),
        )
