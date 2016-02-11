from django.db import models
from django.utils.translation import ugettext_lazy as _


class Person(models.Model):
    STATUS_CHOICES = (
        ('STU', _('Étudiant')),
        ('ADM', _('Administratif')),
        ('PROF', _('Enseignant')),
    )

    last_name = models.CharField(_('Nom'), max_length=35)
    birt_name = models.CharField(_('Nom de naissance'), max_length=35)
    first_name =models.CharField(_('Prénom'), max_length=35)
    status = models.CharField(_('Nom'), max_length=4, choices=STATUS_CHOICES)
    mail = models.EmailField(_('Email'))
    cmp = models.ForeignKey(Institute)
    birth_date = models.DateField(_('Date de naissance'))
    username = models.CharField(_('Identifiant'), max_length=35)
