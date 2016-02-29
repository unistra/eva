from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class ECICommissionMember(models.Model):
    """
    ECI Commission Member model
    """
    MEMBER_TYPE_CHOICES = (
        ('commission', _('Commission ECI')),
        ('tenured', _('Etudiant CFVU titulaire')),
        ('supply', _('Etudiant CFVU suppléant')),
    )

    username = models.CharField(
        _('ID Membre'), max_length=35, unique=True)
    last_name = models.CharField(_('Nom'), max_length=35)
    first_name = models.CharField(_('Prénom'), max_length=35)
    member_type = models.CharField(
        _('Type'), blank=False, choices=MEMBER_TYPE_CHOICES, max_length=20)

    email = models.CharField(_('Mail'), max_length=256)

    def clean_fields(self, exclude=None):
        if self.username in [e.username for e in ECICommissionMember.objects.all()]:
            raise ValidationError(
                {'username': [_("L'identifiant %s est déjà utilisé." \
                 % self.username), ]}
            )

    def __str__(self):
        return '%s %s' % (self.last_name, self.first_name)

    class Meta:
        permissions = (
            ('can_view_eci_commission_member',
             _('Peut voir les membres de la commission ECI')),
        )
