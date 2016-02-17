from django.db import models
from django.utils.translation import ugettext_lazy as _
from ..institute.models import Institute
from django.core.exceptions import ValidationError


class ECICommissionMember(models.Model):
    """
    ECI Commission Member model
    """
    MEMBER_TYPE_CHOICES = (
        ('commission', _('Commission ECI')),
        ('tenured', _('Etudiant CFVU titulaire')),
        ('supply', _('Etudiant CFVU suppléant')),
    )

    id_member = models.CharField(
        _('ID Membre'), max_length=35, unique=True
    )

    last_name = models.CharField(_('Nom'), max_length=35)

    first_name = models.CharField(_('Prénom'), max_length=35)

    member_type = models.CharField(_('Type'), blank=False,
                                   choices=MEMBER_TYPE_CHOICES, max_length=20)

    mail = models.CharField(_('Mail'), max_length=256)

    status = models.CharField(
        _('Statut'), blank=False, max_length=15)

    institute = models.CharField(_('Composante'), max_length=25)

    def __str__(self):
        return '%s %s' % (self.name, self.firstname)

    @property
    def institute_label(self, val):
        a = Institute.objects.get(code=self.status).label
        print(a)
        return a

    class Meta:
        permissions = (
            ('can_view_eci_commission_member',
             _('Peut voir les membres de la commission ECI')),
        )
