from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


class AcademicField(models.Model):
    name = models.CharField(_('Domaine'), max_length=70)

    def __str__(self):
        return self.name


class Staff(models.Model):
    _id = models.CharField(_('ID'), max_length=35)
    _lastname = models.CharField(_('Nom'), max_length=35)
    _firstname = models.CharField(_('Prénom'), max_length=35)
    _mail = models.EmailField(_('Email'))

    def __str__(self):
        return "%s %s" % (self.firstname, self.lastname)


class ScolManager(Staff):
    is_ref_app = models.BooleanField(_("Référent application"))


class Institute(models.Model):
    field_choice = AcademicField.objects.all()

    code = models.CharField(_('Code composante'), max_length=3)
    is_on_duty = models.BooleanField(_('En service'))
    label = models.CharField(_('Libellé composante'), max_length=85)
    field = models.CharField(_('Domaine'), max_length=70, blank=False)
    dircomp = models.ForeignKey(Staff, related_name='dircomp', on_delete=models.CASCADE, blank=True, null=True)
    rac = models.ForeignKey(Staff, related_name='racs', on_delete=models.CASCADE, blank=True, null=True)
    diretu = models.ManyToManyField(Staff, related_name='diretu')
    scol_manager = models.ManyToManyField(ScolManager, related_name='scol_managers')

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
